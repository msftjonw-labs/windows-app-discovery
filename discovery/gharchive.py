"""Uniform random sampling of active public repositories from raw GH Archive hourly files.

GH Archive publishes every public GitHub event as hourly gzip JSON files at
https://data.gharchive.org/. Reading those files directly avoids BigQuery.
Sampling uses bottom-k hashing: each repository receives a pseudo-random key
sha256(seed:repo_id); the k smallest keys form a uniform random sample of the
eligible population. Per-hour bottom-k sets merge exactly, so hours can be
processed independently and in parallel.
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import logging
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

LOG = logging.getLogger("gharchive")
ARCHIVE_URL = "https://data.gharchive.org/{hour}.json.gz"
USER_AGENT = "windows-app-discovery/1.0 (+https://github.com/msftjonw-labs/windows-app-discovery)"
CACHE_VERSION = "gharchive-1"
MAX_MISSING_FRACTION = 0.05
BOT_LOGIN = re.compile(r"\[bot\]$|(?:^|[-_])bot$|^dependabot$|^renovate$", re.I)
QUALIFYING = {
    "IssuesEvent": ({"opened", "reopened"}, "issue_opened"),
    "PullRequestEvent": ({"opened", "reopened"}, "pr_opened"),
    "IssueCommentEvent": ({"created"}, "comment"),
    "PullRequestReviewEvent": ({"created"}, "review"),
    "PullRequestReviewCommentEvent": ({"created"}, "review_comment"),
}
TYPE_MARKERS = tuple(f'"type":"{name}"'.encode() for name in QUALIFYING)


class ArchiveUnavailable(RuntimeError):
    """Raised when too much of the archive window cannot be read."""


def hour_name(moment):
    return f"{moment:%Y-%m-%d}-{moment.hour}"


def window_hours(start, end):
    if start.minute or start.second or end.minute or end.second:
        raise ValueError("GH Archive windows must start and end on whole UTC hours")
    hours, cursor = [], start
    while cursor < end:
        hours.append(cursor)
        cursor += timedelta(hours=1)
    return hours


def sample_key(seed, repo_id):
    return int.from_bytes(hashlib.sha256(f"{seed}:{repo_id}".encode()).digest()[:8], "big")


def is_bot(login):
    return not login or bool(BOT_LOGIN.search(login))


def evidence_url(event):
    repo, payload = event["repo"]["name"], event["payload"]
    kind = event["type"]
    if kind == "IssuesEvent":
        issue = payload.get("issue") or {}
        return issue.get("html_url") or f"https://github.com/{repo}/issues/{issue.get('number', '')}".rstrip("/")
    if kind == "PullRequestEvent":
        number = payload.get("number") or (payload.get("pull_request") or {}).get("number")
        return f"https://github.com/{repo}/pull/{number}" if number else f"https://github.com/{repo}"
    item = payload.get("review") if kind == "PullRequestReviewEvent" else payload.get("comment")
    return (item or {}).get("html_url") or f"https://github.com/{repo}"


def qualifying_event(event):
    """Return (kind, url) for human, public issue/PR activity, otherwise None."""
    rule = QUALIFYING.get(event.get("type"))
    if not rule or event.get("public") is False:
        return None
    actions, kind = rule
    if (event.get("payload") or {}).get("action") not in actions:
        return None
    if is_bot((event.get("actor") or {}).get("login")):
        return None
    url = evidence_url(event)
    if not url.startswith("https://github.com/"):
        return None
    return kind, url


def scan_lines(lines, seed, k, start, end):
    """Reduce one hour of raw events to its population IDs and bottom-k repositories."""
    repos, examined, qualifying = {}, 0, 0
    lower, upper = stamp(start), stamp(end)
    for line in lines:
        examined += 1
        if not any(marker in line[:120] for marker in TYPE_MARKERS):
            continue
        event = json.loads(line)
        created = event.get("created_at", "")
        if not lower <= created < upper:
            continue
        found = qualifying_event(event)
        if not found:
            continue
        qualifying += 1
        kind, url = found
        repo_id = event["repo"]["id"]
        entry = repos.get(repo_id)
        if entry is None:
            entry = repos[repo_id] = {
                "database_id": repo_id, "key": sample_key(seed, repo_id), "name": event["repo"]["name"],
                "last_activity": created, "activity_evidence": url, "kinds": [], "observed_events": 0,
            }
        entry["observed_events"] += 1
        if kind not in entry["kinds"]:
            entry["kinds"].append(kind)
        if created >= entry["last_activity"]:
            entry.update(last_activity=created, activity_evidence=url, name=event["repo"]["name"])
    bottom = sorted(repos.values(), key=lambda item: item["key"])[:k]
    return {"ids": sorted(repos), "bottom": bottom, "events": examined, "qualifying": qualifying}


def stamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fetch_hour(hour, attempts=4):
    request = urllib.request.Request(ARCHIVE_URL.format(hour=hour), headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return gzip.decompress(response.read())
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            failure = error
        except (urllib.error.URLError, TimeoutError, OSError, EOFError) as error:
            failure = error
        if attempt < attempts - 1:
            time.sleep(5 * 2 ** attempt)
    raise ArchiveUnavailable(f"{hour}: {failure}")


def process_hour(moment_text, seed, k, cache_dir):
    """Worker entry point (top level so it can run in a separate process)."""
    moment = datetime.fromisoformat(moment_text)
    hour = hour_name(moment)
    cached = None
    if cache_dir:
        digest = hashlib.sha256(f"{seed}:{k}:{CACHE_VERSION}".encode()).hexdigest()[:16]
        cached = Path(cache_dir) / f"{hour}-{digest}.json.gz"
        if cached.exists():
            return {"hour": hour, "status": "ok", **json.loads(gzip.decompress(cached.read_bytes()))}
    try:
        raw = fetch_hour(hour)
    except ArchiveUnavailable as error:
        return {"hour": hour, "status": "error", "error": str(error)}
    if raw is None:
        return {"hour": hour, "status": "missing"}
    result = scan_lines(raw.splitlines(), seed, k, moment, moment + timedelta(hours=1))
    if cached:
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(gzip.compress(json.dumps(result).encode()))
    return {"hour": hour, "status": "ok", **result}


def merge(results, k):
    """Exact global bottom-k: a globally sampled repo is in the bottom-k of every hour it appears in."""
    population, combined = set(), {}
    for result in results:
        population.update(result["ids"])
        for item in result["bottom"]:
            entry = combined.get(item["database_id"])
            if entry is None:
                combined[item["database_id"]] = {**item, "kinds": list(item["kinds"])}
                continue
            entry["observed_events"] += item["observed_events"]
            entry["kinds"] = sorted(set(entry["kinds"]) | set(item["kinds"]))
            if item["last_activity"] >= entry["last_activity"]:
                entry.update(last_activity=item["last_activity"],
                             activity_evidence=item["activity_evidence"], name=item["name"])
    sample = sorted(combined.values(), key=lambda item: item["key"])[:k]
    for rank, item in enumerate(sample, 1):
        item["sample_rank"] = rank
        item["activity_types"] = sorted(item.pop("kinds"))
        item["sample_key"] = f"{item.pop('key'):016x}"
    return sample, len(population)


def discover(start, end, seed, reserve=300, workers=6, cache_dir=None, max_missing=MAX_MISSING_FRACTION):
    """Return (candidates in random order, coverage). Raises ArchiveUnavailable if too many hours are missing."""
    hours = window_hours(start, end)
    results, missing, errors = [], [], []
    began = time.monotonic()
    executor = ProcessPoolExecutor(max_workers=workers) if workers > 1 else ThreadPoolExecutor(max_workers=1)
    with executor as pool:
        futures = [pool.submit(process_hour, hour.isoformat(), seed, reserve, str(cache_dir) if cache_dir else None)
                   for hour in hours]
        for done, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result["status"] == "ok":
                results.append(result)
            elif result["status"] == "missing":
                missing.append(result["hour"])
            else:
                errors.append(result["hour"])
                LOG.warning("GH Archive hour unavailable: %s", result["error"])
            if done % 24 == 0 or done == len(hours):
                LOG.info("GH Archive: %s/%s hours processed (%.0fs)", done, len(hours), time.monotonic() - began)
            if (len(missing) + len(errors)) > max_missing * len(hours):
                for pending in futures:
                    pending.cancel()
                raise ArchiveUnavailable(
                    f"{len(missing)} missing and {len(errors)} unreadable of {len(hours)} GH Archive hours")
    sample, population = merge(results, reserve)
    coverage = {
        "archive": "https://www.gharchive.org/ (raw hourly files, no BigQuery)",
        "seed": seed, "sampling": "bottom-k sha256(seed:repository_id); uniform without replacement",
        "population_size": population, "reserve_candidates": len(sample),
        "hours_expected": len(hours), "hours_processed": len(results),
        "missing_hours": sorted(missing), "unreadable_hours": sorted(errors),
        "events_scanned": sum(result["events"] for result in results),
        "qualifying_events": sum(result["qualifying"] for result in results),
        "archive_seconds": round(time.monotonic() - began, 1),
    }
    return sample, coverage
