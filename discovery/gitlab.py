"""Discover and analyze a bounded cohort of public GitLab.com projects."""

import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import io
import json
import logging
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import time
import urllib.error
from urllib.parse import quote, urlencode
import urllib.request
import zipfile

from discovery import cross_os, pilot, semgrep, windows_container
from discovery.rules import RULESET_VERSION

LOG = logging.getLogger("gitlab")
HOST = "https://gitlab.com"
API = HOST + "/api/v4"
ACTIVITY = (
    "Public GitLab project events: issue/merge-request openings or reopenings, "
    "conversation notes, and merge-request approvals, timestamp-filtered to the window. "
    "System notes and identified bots excluded; non-bot accounts may still automate. "
    "Not equivalent to GitHub's GH Archive sampling frame."
)


class Client:
    def __init__(self, token=None):
        self.token = token
        self.next_request = 0
        self.next_archive = 0
        self.rate_limit_wait = 0
        self.rate_limit_error = None

    @staticmethod
    def cooldown(headers):
        """Respect server cooldowns without shortening long Retry-After values."""
        now = time.time()
        delays = []
        retry = headers.get("Retry-After")
        if isinstance(retry, str):
            try:
                delay = float(retry)
            except ValueError:
                try:
                    delay = parsedate_to_datetime(retry).timestamp() - now
                except (ValueError, TypeError, OverflowError):
                    delay = 0
            if math.isfinite(delay):
                delays.append(max(0, delay))
        for key in ("RateLimit-Reset", "X-RateLimit-Reset"):
            reset = headers.get(key)
            if isinstance(reset, str):
                try:
                    delay = float(reset) - now + 1
                except ValueError:
                    continue
                if math.isfinite(delay):
                    delays.append(max(0, delay))
        return max(delays, default=0)

    def wait(self, archive):
        delay = max(self.next_request, self.next_archive if archive else 0) - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        now = time.monotonic()
        self.next_request = now + (0.5 if self.token else 1)
        if archive:
            self.next_archive = now + 15

    def get(self, endpoint, *, binary=False, maximum=12 * 1024 * 1024, **params):
        if not endpoint.startswith("/") or endpoint.startswith("//"):
            raise ValueError("GitLab API endpoint must be a relative absolute path")
        if self.rate_limit_error:
            raise pilot.PilotError(self.rate_limit_error)
        url = API + endpoint + ("?" + urlencode(params) if params else "")
        headers = {"User-Agent": "windows-app-discovery", "Accept": "application/json"}
        server_errors = 0
        archive = endpoint.endswith("/repository/archive.zip")
        for attempt in range(6):
            self.wait(archive)
            try:
                request = urllib.request.Request(url, headers=headers)
                if self.token:
                    request.add_unredirected_header("PRIVATE-TOKEN", self.token)
                with urllib.request.urlopen(request, timeout=90) as response:
                    data = response.read(maximum + 1)
                    remaining = response.headers.get("RateLimit-Remaining")
                    if remaining is None:
                        remaining = response.headers.get("X-RateLimit-Remaining")
                    if remaining == "0":
                        delay = self.cooldown(response.headers) or 60
                        self.next_request = max(self.next_request, time.monotonic() + delay)
                if len(data) > maximum:
                    raise pilot.DownloadLimitError(f"GitLab response exceeds {maximum} bytes: {endpoint}")
                return data if binary else json.loads(data)
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    delay = max(self.cooldown(error.headers), min(600, 60 * 2 ** attempt))
                    if attempt == 5 or self.rate_limit_wait + delay > 1800:
                        self.rate_limit_error = (
                            f"GitLab API HTTP 429: rate-limit recovery exhausted at {endpoint}; "
                            "further requests stopped. Retry later or configure a read-only GITLAB_TOKEN."
                        )
                        raise pilot.PilotError(self.rate_limit_error) from error
                    self.rate_limit_wait += delay
                    self.next_request = max(self.next_request, time.monotonic() + delay)
                    LOG.warning("GitLab HTTP 429; cooling down all requests for %.0fs before retrying %s "
                                "(attempt %s/6)", delay, endpoint, attempt + 2)
                    continue
                server_errors += 1
                if error.code not in {500, 502, 503, 504} or server_errors >= 3 or attempt == 5:
                    raise pilot.PilotError(f"GitLab API HTTP {error.code}: {endpoint}") from error
                delay = max(self.cooldown(error.headers), 5 * server_errors)
                LOG.warning("GitLab HTTP %s; retrying %s in %ss", error.code, endpoint, delay)
                self.next_request = max(self.next_request, time.monotonic() + delay)
        raise AssertionError("Unreachable")


def project_url(project):
    path = project["path_with_namespace"]
    if not isinstance(path, str) or not path or any(p in {"", ".", ".."} for p in path.split("/")):
        raise pilot.PilotError("Invalid GitLab project path")
    return HOST + "/" + quote(path, safe="/")


def qualifying_event(event, start, end):
    timestamp = event.get("created_at")
    author = event.get("author") or {}
    username = author.get("username", "")
    if (not timestamp or not start <= pilot.parse_time(timestamp) < end or not username
            or author.get("bot") or pilot.gharchive.is_bot(username)
            or re.search(r"(?:^|[_-])bot(?:$|[_-])|^project_\d+_bot", username, re.I)):
        return None
    action, target = event.get("action_name"), event.get("target_type")
    note = event.get("note") or {}
    if action in {"opened", "reopened"} and target in {"Issue", "MergeRequest"}:
        kind = action
    elif action == "commented on" and note.get("noteable_type") in {"Issue", "MergeRequest"} and not note.get("system"):
        kind = "comment"
    elif action == "approved" and target == "MergeRequest":
        kind = "approval"
    else:
        return None
    return {"timestamp": timestamp, "kind": kind, "event_id": event["id"],
            "target_type": note.get("noteable_type", target),
            "target_iid": note.get("noteable_iid") or event.get("target_iid")}


def discover(client, limit, start, end, project_budget=500, event_pages=2):
    candidates, seen = [], set()
    coverage = {
        "mode": "bounded-gitlab", "representative_sample": False,
        "activity": ACTIVITY, "requested_limit": limit, "project_budget": project_budget,
        "event_pages_per_project": event_pages, "projects_examined": 0, "events_examined": 0,
        "event_history_bounded": [], "discovery_errors": [], "selection_order": "last_activity_at descending",
    }
    stop = False
    for page in range(1, (project_budget + 99) // 100 + 1):
        projects = client.get("/projects", visibility="public", order_by="last_activity_at",
                              sort="desc", per_page=100, page=page, simple=True)
        if not projects:
            break
        for project in projects:
            if coverage["projects_examined"] >= project_budget or len(candidates) >= limit:
                stop = True
                break
            if project["id"] in seen:
                continue
            seen.add(project["id"])
            coverage["projects_examined"] += 1
            if pilot.parse_time(project["last_activity_at"]) < start:
                stop = True
                break
            if project.get("visibility") != "public":
                continue
            events = {}
            try:
                for event_page in range(1, event_pages + 1):
                    entries = client.get(
                        f"/projects/{project['id']}/events",
                        after=(start - timedelta(days=1)).date().isoformat(),
                        before=(end + timedelta(days=1)).date().isoformat(),
                        sort="desc", per_page=100, page=event_page)
                    coverage["events_examined"] += len(entries)
                    for entry in entries:
                        event = qualifying_event(entry, start, end)
                        if event:
                            event["url"] = project_url(project)
                            if event["target_iid"]:
                                section = "issues" if event["target_type"] == "Issue" else "merge_requests"
                                event["url"] += f"/-/{section}/{int(event['target_iid'])}"
                            events[event["event_id"]] = event
                    if len(entries) < 100:
                        break
                    if event_page == event_pages:
                        coverage["event_history_bounded"].append(project["path_with_namespace"])
            except (pilot.PilotError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
                LOG.error("GitLab discovery %s: %s", project["path_with_namespace"], error)
                coverage["discovery_errors"].append({"project": project["path_with_namespace"], "error": str(error)})
                continue
            if events:
                evidence = sorted(events.values(), key=lambda event: pilot.parse_time(event["timestamp"]), reverse=True)
                candidates.append({
                    "project_id": project["id"], "name": project["path_with_namespace"],
                    "url": project_url(project), "last_activity": evidence[0]["timestamp"],
                    "observed_events": len(evidence), "activity_types": sorted({e["kind"] for e in evidence}),
                    "activity_evidence": evidence[:20],
                })
        if stop or len(projects) < 100:
            break
    coverage["bounded"] = True
    coverage["cohort_size"] = len(candidates)
    return candidates, coverage


def document_evidence(data, url, sha):
    """Read bounded UTF-8 documentation directly from the pinned archive."""
    limits, sources, total, evidence_size = [], [], 0, 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 100000:
            raise pilot.PilotError("Archive has too many entries")
        candidates = []
        for member in members:
            path = pilot.safe_path(member.filename)
            if member.is_dir() or len(path.parts) < 2 or stat.S_ISLNK(member.external_attr >> 16):
                continue
            relative = PurePosixPath(*path.parts[1:])
            if not cross_os.eligible_document(relative) or pilot.is_ci_file(relative):
                continue
            candidates.append((relative, member))
        candidates.sort(key=lambda pair: (
            not (len(pair[0].parts) == 1 and pair[0].name.lower().startswith("readme")),
            len(pair[0].parts), str(pair[0])))
        reviewed = 0
        for path, member in candidates:
            if member.file_size > cross_os.MAX_FILE_BYTES:
                limits.append(f"Oversize evidence file omitted: {path}")
                continue
            if reviewed >= cross_os.MAX_DOCUMENTS or total + member.file_size > cross_os.MAX_SOURCE_BYTES:
                limits.append("Document count or source byte bound reached")
                break
            reviewed += 1
            total += member.file_size
            try:
                content = archive.read(member).decode("utf-8-sig")
            except UnicodeDecodeError:
                limits.append(f"Non-UTF-8 evidence file omitted: {path}")
                continue
            if any(ord(char) < 32 and char not in "\t\n\r" for char in content):
                limits.append(f"Binary evidence file omitted: {path}")
                continue
            lines = content.splitlines()
            wanted = set(range(min(20, len(lines))))
            for index, line in enumerate(lines):
                if cross_os.OS_PATTERN.search(line):
                    wanted.update(range(max(0, index - 3), min(len(lines), index + 5)))
            excerpt, length = [], 0
            for index in sorted(wanted):
                line = lines[index]
                if length + len(line) > 8000 or evidence_size + len(line) > cross_os.MAX_EVIDENCE_CHARS:
                    limits.append(f"Evidence excerpt bounded: {path}")
                    break
                excerpt.append({"line": index + 1, "text": line})
                length += len(line)
                evidence_size += len(line)
            if excerpt:
                sources.append({
                    "id": f"S{len(sources) + 1}", "path": str(path),
                    "url": f"{url}/-/blob/{sha}/{quote(str(path), safe='/')}", "lines": excerpt,
                })
    for limitation in sorted(set(limits)):
        LOG.warning("%s: %s", url, limitation)
    return {"sources": sources, "limitations": sorted(set(limits))}


def analyze_repository(client, candidate, inspector):
    project_id = candidate["project_id"]
    project = client.get(f"/projects/{project_id}")
    if project.get("visibility") != "public":
        raise pilot.RepositoryUnavailable("GitLab project is no longer public")
    branch = project.get("default_branch")
    if not branch:
        raise pilot.PilotError("GitLab project has no default branch")
    commit = client.get(f"/projects/{project_id}/repository/commits/{quote(branch, safe='')}")
    sha = commit["id"]
    if not re.fullmatch(r"[a-fA-F0-9]{40,64}", sha):
        raise pilot.PilotError("Invalid GitLab commit SHA")
    url = project_url(project)
    languages = client.get(f"/projects/{project_id}/languages")
    data = client.get(f"/projects/{project_id}/repository/archive.zip", sha=sha,
                      binary=True, maximum=pilot.MAX_DOWNLOAD)
    scratch = pilot.ROOT / ".cache" / "gitlab-work"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gitlab-", dir=scratch) as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        files, skipped = pilot.extract_sources(data, source)
        analysis = pilot.analyze_sources(files, skipped, "gitlab-archive", source, inspector, work,
                                         engine_config=semgrep.identity(None, work))
        evidence = document_evidence(data, url, sha)
    return {
        **candidate, "id": f"gitlab:{project_id}", "name": project["path_with_namespace"], "url": url,
        "sha": sha, "fork": bool(project.get("forked_from_project")), "archived": project.get("archived", False),
        "primary_language": max(languages, key=languages.get) if languages else "Unknown",
        "languages": languages, "language_units": "percent (GitLab API)", "languages_truncated": False,
        **analysis,
        "cross_os": {
            "version": cross_os.VERSION, "sha": sha, "generated_at": pilot.stamp(datetime.now(timezone.utc)),
            "status": "success", **cross_os.classify(evidence),
            "documents_reviewed": len(evidence["sources"]), "limitations": evidence["limitations"],
        },
    }


def collect(client, limit, start, end, inspector, project_budget=500, event_pages=2):
    candidates, coverage = discover(client, limit, start, end, project_budget, event_pages)
    records = []
    for candidate in candidates:
        LOG.info("Analyzing GitLab project %s", candidate["name"])
        try:
            record = analyze_repository(client, candidate, inspector)
        except (pilot.PilotError, urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError,
                subprocess.TimeoutExpired, zipfile.BadZipFile) as error:
            LOG.error("%s: %s", candidate["name"], error)
            record = {**candidate, "status": "failed", "error": str(error),
                      "cross_os": {"status": "failed", "error": str(error)}}
        records.append(record)
    report = {
        "schema_version": 1, "source_platform": "GitLab", "ruleset_version": RULESET_VERSION,
        "inspector_version": pilot.INSPECTOR_VERSION, "generated_at": pilot.stamp(datetime.now(timezone.utc)),
        "window": {"start": pilot.stamp(start), "end": pilot.stamp(end)},
        "coverage": coverage, "repositories": records, "metrics": pilot.aggregate(records),
    }
    report["metrics"]["cross_os"] = cross_os.summary(report)
    windows_container.analyze_report(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--end", help="Timezone-qualified end of the 30-day activity window")
    parser.add_argument("--project-budget", type=int, default=500)
    parser.add_argument("--event-pages", type=int, default=2)
    parser.add_argument("--inspector", type=Path)
    parser.add_argument("--install-inspector", action="store_true")
    parser.add_argument("--output", type=Path, default=pilot.ROOT / "gitlab-reports" / "latest.json")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if not 1 <= args.limit <= 100 or not args.limit <= args.project_budget <= 1000 or not 1 <= args.event_pages <= 5:
        parser.error("Require 1 <= limit <= 100, limit <= project-budget <= 1000, and 1 <= event-pages <= 5")
    inspector = pilot.install_inspector(pilot.ROOT / ".tools" / "inspector") if args.install_inspector else args.inspector
    if inspector is None:
        matches = list((pilot.ROOT / ".tools" / "inspector").rglob("ApplicationInspector.CLI.exe"))
        inspector = matches[0] if len(matches) == 1 else None
    if not inspector or not inspector.is_file():
        parser.error("Use --install-inspector on Windows x64 or --inspector PATH")
    end = pilot.parse_time(args.end) if args.end else datetime.now(timezone.utc)
    report = collect(Client(os.environ.get("GITLAB_TOKEN")), args.limit, end - timedelta(days=30), end,
                     inspector.resolve(), args.project_budget, args.event_pages)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending = args.output.with_suffix(".tmp")
    pending.write_text(json.dumps(report, indent=2), encoding="utf-8")
    pending.replace(args.output)
    cross_os.write_assessments(report, args.output.with_name("cross-os-assessments.json"))
    if not report["metrics"]["successful"] or not report["metrics"]["cross_os"]["complete"]:
        raise pilot.PilotError("GitLab collection incomplete; diagnostics saved, publishing withheld")
    LOG.info("Wrote %s", args.output)


if __name__ == "__main__":
    try:
        main()
    except (pilot.PilotError, urllib.error.URLError, TimeoutError, ValueError) as error:
        LOG.error("%s", error)
        raise SystemExit(1) from error
