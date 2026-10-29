"""Run with: python -m discovery.pilot --help (standard library only)."""

import argparse
from collections import Counter
import codecs
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import logging
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from statistics import NormalDist
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from urllib.parse import quote
import zipfile

from discovery import gharchive
from discovery import semgrep as semgrep_engine
from discovery.projects import APPLICATION_TYPES, classify_projects
from discovery.windows_container import base_images
from discovery.rules import (
    COMPILED, COMPILED_FILE_RULES, COMPONENTS, EXCLUDED_DIRS, EXTENSIONS,
    EXTENSIONLESS_NAMES, GENERATED_NAMES, JSON_MANIFEST, OS_TARGETS, RULES, RULESET_VERSION,
    inspector_rules, primary_framework, primary_platform,
)

LOG = logging.getLogger("pilot")
ROOT = Path(__file__).resolve().parents[1]
MAX_DOWNLOAD = 150 * 1024 * 1024
MAX_EXTRACTED = 256 * 1024 * 1024
MAX_FILE = 8 * 1024 * 1024
MAX_FILES = 20000
MAX_SELECTED_FILES = 10000
PARTIAL_REASONS = {
    "oversize_files", "unsupported_encoding", "truncated_tree",
    "selected_file_limit", "extraction_limit",
}
INSPECTOR_VERSION = "1.10.2"
INSPECTOR_STRATEGY = "bounded-batches-1"
MAX_INSPECTOR_FILES = 100
MAX_INSPECTOR_BYTES = 8 * 1024 * 1024
INSPECTOR_SHA256 = "a343cf8fcdca9e3e93b5fd2c12b5381b70abab578aad7d45a8561b7a7301fc07"

SEARCH = """
query($search: String!, $cursor: String, $count: Int!) {
  search(query:$search, type:ISSUE, first:$count, after:$cursor) {
    issueCount pageInfo { hasNextPage endCursor }
    nodes {
      ... on Issue {
        createdAt url author { __typename login }
        repository { id nameWithOwner isPrivate }
        comments(last:20) {
          pageInfo { hasPreviousPage }
          nodes { createdAt url author { __typename login } }
        }
      }
      ... on PullRequest {
        createdAt url author { __typename login }
        repository { id nameWithOwner isPrivate }
        comments(last:20) {
          pageInfo { hasPreviousPage }
          nodes { createdAt url author { __typename login } }
        }
        reviews(last:20) {
          pageInfo { hasPreviousPage }
          nodes { submittedAt url author { __typename login } }
        }
      }
    }
  }
}"""
METADATA = """
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    id databaseId nameWithOwner url isPrivate isFork isArchived
    primaryLanguage { name }
    languages(first:100, orderBy:{field:SIZE,direction:DESC}) {
      totalSize pageInfo { hasNextPage }
      edges { size node { name } }
    }
    defaultBranchRef { target { ... on Commit { oid } } }
  }
}"""


class PilotError(RuntimeError):
    pass


class DownloadLimitError(PilotError):
    pass


class RepositoryUnavailable(PilotError):
    """The sampled repository was deleted, made private, or cannot be resolved."""


def stamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def graphql(document, allow_missing=False, **variables):
    command = ["gh", "api", "graphql", "-f", f"query={document}"]
    for key, value in variables.items():
        if value is not None:
            command += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    for attempt in range(3):
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=120)
        body = None
        if result.stdout.strip().startswith("{"):
            body = json.loads(result.stdout)
        errors = (body or {}).get("errors")
        if allow_missing and errors and body.get("data") is not None and all(
                error.get("type") == "NOT_FOUND" for error in errors):
            return body["data"]
        if result.returncode == 0:
            if errors:
                raise PilotError(f"GraphQL errors: {errors}")
            return body["data"]
        message = result.stderr.strip()
        if attempt < 2 and any(word in message.lower() for word in ("rate limit", "502", "503", "timeout")):
            LOG.warning("GraphQL transient failure; retrying: %s", message)
            time.sleep(30 * (attempt + 1))
            continue
        raise PilotError(f"GraphQL request failed: {message}")
    raise AssertionError("Unreachable")


def human(actor):
    return bool(
        actor and actor.get("__typename") == "User"
        and not gharchive.is_bot(actor["login"])
    )


def qualifying_events(node, start, end):
    events = [(node["createdAt"], node.get("author"), node["url"], "opened")]
    events += [(c["createdAt"], c.get("author"), c["url"], "comment")
               for c in node["comments"]["nodes"]]
    events += [(r["submittedAt"], r.get("author"), r["url"], "review")
               for r in node.get("reviews", {}).get("nodes", []) if r["submittedAt"]]
    return [
        {"timestamp": timestamp, "url": url, "kind": kind}
        for timestamp, actor, url, kind in events
        if start <= parse_time(timestamp) < end and human(actor)
    ]


def discover(limit, start, end):
    repos = {}
    coverage = {"searches": [], "items_examined": 0, "truncated_connections": 0}
    # Equal issue/PR budgets avoid taking the entire cohort from one activity type.
    budget = min(limit * 2, 500)
    for kind in ("issue", "pr"):
        cursor = None
        examined = 0
        query = f"is:public is:{kind} updated:>={stamp(start)} updated:<{stamp(end)} sort:updated-desc"
        while examined < budget:
            page = graphql(SEARCH, search=query, cursor=cursor, count=min(50, budget - examined))["search"]
            nodes = page["nodes"]
            if not nodes:
                break
            for node in nodes:
                examined += 1
                coverage["items_examined"] += 1
                for connection in ("comments", "reviews"):
                    if node.get(connection, {}).get("pageInfo", {}).get("hasPreviousPage"):
                        coverage["truncated_connections"] += 1
                repository = node["repository"]
                events = qualifying_events(node, start, end)
                if repository["isPrivate"] or not events:
                    continue
                entry = repos.setdefault(repository["id"], {
                    "name": repository["nameWithOwner"], "events": {},
                })
                for event in events:
                    entry["events"][event["url"] + event["timestamp"]] = event
            cursor = page["pageInfo"]["endCursor"]
            if not page["pageInfo"]["hasNextPage"]:
                break
        coverage["searches"].append({
            "query": query, "items_examined": examined,
            "matching_items": page["issueCount"],
            "bounded": page["pageInfo"]["hasNextPage"] or page["issueCount"] > examined,
        })
    candidates = []
    for entry in repos.values():
        events = list(entry["events"].values())
        candidates.append({
            "name": entry["name"], "last_activity": max(e["timestamp"] for e in events),
            "activity_types": sorted({e["kind"] for e in events}),
            "observed_events": len(events),
            "activity_evidence": max(events, key=lambda e: e["timestamp"])["url"],
        })
    coverage["eligible_repositories"] = len(candidates)
    return sorted(candidates, key=lambda r: r["last_activity"], reverse=True)[:limit], coverage


def download(url, maximum):
    request = urllib.request.Request(url, headers={"User-Agent": "windows-app-discovery-pilot"})
    with urllib.request.urlopen(request, timeout=90) as response:
        if int(response.headers.get("Content-Length", 0)) > maximum:
            raise DownloadLimitError(f"Download exceeds {maximum} byte limit")
        data = response.read(maximum + 1)
    if len(data) > maximum:
        raise DownloadLimitError(f"Download exceeds {maximum} byte limit")
    return data


def install_inspector(destination):
    """Install Microsoft's pinned, checksum-verified Windows x64 release."""
    name = f"ApplicationInspector_win_{INSPECTOR_VERSION}.zip"
    url = f"https://github.com/microsoft/ApplicationInspector/releases/download/v{INSPECTOR_VERSION}/{name}"
    data = download(url, 200 * 1024 * 1024)
    if hashlib.sha256(data).hexdigest() != INSPECTOR_SHA256:
        raise PilotError("Application Inspector release checksum mismatch")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            safe_path(info.filename)
        archive.extractall(destination)
    matches = list(destination.rglob("ApplicationInspector.CLI.exe"))
    if len(matches) != 1:
        raise PilotError("Expected one ApplicationInspector.CLI.exe in release")
    return matches[0]


def safe_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise PilotError(f"Unsafe archive path: {name}")
    return path


CI_PATH = re.compile(
    r"(?:\.github/workflows/[^/]+\.ya?ml|\.?appveyor\.ya?ml|azure-pipelines\.ya?ml|\.gitlab-ci\.ya?ml"
    r"|\.circleci/config\.ya?ml)", re.I)
CI_SYSTEMS = (("GitHub Actions", ".github/workflows/"), ("AppVeyor", "appveyor"),
              ("Azure Pipelines", "azure-pipelines"), ("GitLab CI", ".gitlab-ci"), ("CircleCI", ".circleci/"))
CI_WINDOWS_LINE = re.compile(
    r"windows-(?:latest|\d{2,4})|\bGOOS\s*[:=]\s*['\"]?windows|\bVisual Studio\b"
    r"|(?:runs-on|vmImage|\bos\b|\bimage\b|platform|executor|goos|matrix)\b.*\bwindows\b"
    r"|^\s*-\s*['\"]?windows[-\w.]*['\"]?\s*$", re.I)
CI_TEST_COMMAND = re.compile(r"\b(?:pytest|unittest|tox|nox|go\s+test|go\s+build|npm\s+(?:run\s+)?test|dotnet\s+test|"
                             r"cargo\s+test|ctest|mvn\s+test|gradlew?\s+test)\b", re.I)


def is_ci_file(path):
    return bool(CI_PATH.fullmatch(path if isinstance(path, str) else path.as_posix()))


def ci_signals(ci_files):
    """Windows CI evidence from workflow/pipeline config. It shows intent to build/test on Windows, not run results."""
    systems = set()
    windows_systems = set()
    evidence = []
    tests = False
    for path, text in ci_files:
        system = next((name for name, marker in CI_SYSTEMS if marker in path.lower()), "CI")
        systems.add(system)
        for number, line in enumerate(text.split("\n"), 1):
            if line.lstrip().startswith("#"):
                continue
            if CI_TEST_COMMAND.search(line):
                tests = True
            if CI_WINDOWS_LINE.search(line):
                windows_systems.add(system)
                if len(evidence) < 10:
                    evidence.append({"path": path, "line": number, "system": system, "excerpt": line.strip()[:120]})
    return {"systems": sorted(systems), "windows": bool(windows_systems), "windows_systems": sorted(windows_systems),
            "runs_tests": tests, "evidence": evidence}


def source_exclusion(path):
    if is_ci_file(path):
        return None
    if any(part.lower() in EXCLUDED_DIRS for part in path.parts[:-1]):
        return "excluded_directories"
    name = path.name.lower()
    if name in GENERATED_NAMES or name.endswith((
        ".g.cs", ".designer.cs", ".min.js", ".generated.cs", ".js.map", ".css.map",
    )):
        return "generated"
    if path.suffix.lower() in {".json", ".jsonc"} and not JSON_MANIFEST.fullmatch(name):
        return "data_assets"
    if path.suffix.lower() == ".txt" and name != "cmakelists.txt" and not re.fullmatch(r"requirements[\w.-]*\.txt", name):
        return "data_assets"
    if name in EXTENSIONLESS_NAMES or name == "go.mod" or name.startswith("dockerfile."):
        return None
    if path.suffix.lower() not in EXTENSIONS:
        return "unsupported_extensions"
    return None


def store_source(relative, raw, destination, files, skipped):
    try:
        if raw.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
            text = raw.decode("utf-32")
        elif raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            text = raw.decode("utf-16")
        elif len(raw) >= 4 and len(raw) % 2 == 0 and (
            raw[1::2].count(0) > len(raw) / 4 or raw[::2].count(0) > len(raw) / 4
        ):
            # BOM-less UTF-16 source generally has a zero byte in most ASCII pairs.
            encoding = "utf-16-le" if raw[1::2].count(0) > raw[::2].count(0) else "utf-16-be"
            text = raw.decode(encoding)
        else:
            text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        skipped["unsupported_encoding"] += 1
        return
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        skipped["binary"] += 1
        return
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    target = destination.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    files.append((relative.as_posix(), text))


def extract_sources(data, destination):
    files = []
    skipped = Counter()
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 100000:
            raise PilotError("Archive has too many entries")
        for info in members:
            path = safe_path(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                skipped["symlinks"] += 1
                continue
            if info.is_dir() or len(path.parts) < 2:
                continue
            relative = PurePosixPath(*path.parts[1:])
            reason = source_exclusion(relative)
            if reason:
                skipped[reason] += 1
                continue
            if info.file_size > MAX_FILE:
                skipped["oversize_files"] += 1
                continue
            total += info.file_size
            if total > MAX_EXTRACTED or len(files) >= MAX_FILES:
                raise PilotError("Source extraction exceeds pilot resource limits")
            store_source(relative, archive.read(info), destination, files, skipped)
    return files, dict(skipped)


def selected_sources(repository, sha, destination):
    endpoint = f"repos/{repository}/git/trees/{sha}?recursive=1"
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True,
                            encoding="utf-8", timeout=120)
    if result.returncode:
        raise PilotError(f"Source tree request failed: {result.stderr.strip()}")
    tree = json.loads(result.stdout)
    skipped = Counter()
    if tree["truncated"]:
        skipped["truncated_tree"] += 1
        LOG.warning("%s: GitHub returned a truncated source tree", repository)
    candidates = []
    for entry in tree["tree"]:
        path = safe_path(entry["path"])
        if entry["mode"] == "120000":
            skipped["symlinks"] += 1
            continue
        if entry["mode"] == "160000":
            skipped["submodules"] += 1
            continue
        if entry["type"] != "blob":
            continue
        reason = source_exclusion(path)
        if reason:
            skipped[reason] += 1
            continue
        size = entry["size"]
        if not isinstance(size, int) or size < 0:
            raise PilotError(f"Invalid source tree size: {path}")
        if size > MAX_FILE:
            skipped["oversize_files"] += 1
            continue
        candidates.append((path, size, entry["sha"]))
    manifests = {".csproj", ".vbproj", ".fsproj", ".vcxproj", ".props", ".targets", ".pbxproj"}
    candidates.sort(key=lambda item: (
        not (item[0].suffix.lower() in manifests or item[0].name.lower() in {
            "package.json", "cargo.toml", "pubspec.yaml", "cmakelists.txt",
            "androidmanifest.xml", "appxmanifest.xml",
        }), item[0].as_posix(),
    ))
    selected = []
    total = 0
    for path, size, oid in candidates:
        if len(selected) >= MAX_SELECTED_FILES:
            skipped["selected_file_limit"] += 1
        elif total + size > MAX_EXTRACTED:
            skipped["extraction_limit"] += 1
        else:
            selected.append((path, size, oid))
            total += size
    files = []
    batch = []
    batch_bytes = 0
    for entry in selected + [None]:
        if batch and (entry is None or len(batch) >= 40 or batch_bytes + entry[1] > 4 * 1024 * 1024):
            for (path, _, _), raw in zip(batch, fetch_source_batch(repository, sha, batch)):
                if raw is None:
                    skipped["oversize_files"] += 1
                    continue
                store_source(path, raw, destination, files, skipped)
            batch = []
            batch_bytes = 0
        if entry is not None:
            batch.append(entry)
            batch_bytes += entry[1]
    return files, dict(skipped)


def fetch_source_batch(repository, sha, entries):
    owner, name = repository.split("/")
    variables = {"owner": owner, "name": name}
    declarations = ["$owner:String!", "$name:String!"]
    fields = []
    for index, (_, _, oid) in enumerate(entries):
        declarations.append(f"$oid{index}:GitObjectID!")
        variables[f"oid{index}"] = oid
        fields.append(f"b{index}:object(oid:$oid{index}) {{ ... on Blob {{ text isBinary isTruncated byteSize }} }}")
    document = "query(" + ",".join(declarations) + ") { repository(owner:$owner,name:$name) {" + " ".join(fields) + "} }"
    blobs = graphql(document, **variables)["repository"]
    if blobs is None:
        raise PilotError("Repository is no longer accessible during source retrieval")
    results = []
    for index, (path, size, _) in enumerate(entries):
        blob = blobs[f"b{index}"]
        if blob is None:
            raise PilotError(f"Pinned source blob is missing: {path}")
        text = blob.get("text")
        if (isinstance(text, str) and not blob["isBinary"] and not blob["isTruncated"]
                and "\ufffd" not in text and len(text.encode("utf-8")) == size):
            raw = text.encode("utf-8")
        else:
            url = f"https://raw.githubusercontent.com/{repository}/{sha}/{quote(path.as_posix())}"
            try:
                raw = download(url, MAX_FILE)
            except DownloadLimitError:
                LOG.warning("%s: source exceeded file limit: %s", repository, path)
                raw = None
        if raw is not None and len(raw) > MAX_FILE:
            LOG.warning("%s: source exceeded file limit: %s", repository, path)
            raw = None
        results.append(raw)
    return results


def acquire_sources(repository, sha, destination):
    try:
        data = download(f"https://codeload.github.com/{repository}/zip/{sha}", MAX_DOWNLOAD)
    except DownloadLimitError:
        LOG.warning("%s: archive exceeds limit; switching to bounded source-file retrieval", repository)
        files, skipped = selected_sources(repository, sha, destination)
        return files, skipped, "selected-files"
    files, skipped = extract_sources(data, destination)
    return files, skipped, "archive"


def classify(files):
    labels = {"platform": set(), "framework": set(), "component": set()}
    evidence = []
    executable = False
    for path, text in files:
        if re.search(r"<OutputType>\s*(?:WinExe|Exe)\s*</OutputType>|<ConfigurationType>\s*Application|com\.android\.application|Microsoft\.NET\.Sdk\.Web|\badd_executable\s*\(|(?m:^\s*package\s+main\b)|if\s+__name__\s*==\s*['\"]__main__['\"]", text, re.I):
            executable = True
        if path.endswith("package.json"):
            try:
                package = json.loads(text)
            except json.JSONDecodeError as error:
                LOG.warning("Invalid package manifest %s; application entry ignored: %s", path, error)
            else:
                if not isinstance(package, dict):
                    raise PilotError(f"Package manifest is not an object: {path}")
                dependencies = package.get("dependencies") or {}
                dev_dependencies = package.get("devDependencies") or {}
                if not isinstance(dependencies, dict) or not isinstance(dev_dependencies, dict):
                    raise PilotError(f"Package dependencies are not objects: {path}")
                if package.get("main") and "electron" in (dependencies | dev_dependencies):
                    executable = True
                if package.get("bin"):
                    executable = True
        for key, label, path_pattern, pattern in COMPILED_FILE_RULES:
            match = pattern.search(text) if path_pattern.search(path) else None
            if match:
                labels["platform"].add(label)
                evidence.append({"rule": key, "kind": "platform", "label": label, "path": path,
                                 "line": text.count("\n", 0, match.start()) + 1,
                                 "engine": "file-scoped runtime/deployment indicator"})
        for key, kind, label, pattern in COMPILED:
            match = pattern.search(text)
            if match:
                labels[kind].add(label)
                evidence.append({
                    "rule": key, "kind": kind, "label": label, "path": path,
                    "line": text.count("\n", 0, match.start()) + 1,
                    "engine": "manifest/source heuristic",
                })
        # Platform-specific directories are supporting evidence for cross-platform apps.
        if any(part.lower() == "windows" for part in PurePosixPath(path).parts[:-1]):
            labels["platform"].add("Windows")
            evidence.append({"rule": "windows-directory", "kind": "platform", "label": "Windows",
                             "path": path, "line": 1, "engine": "directory heuristic"})
    # Windows-only frameworks are stronger evidence than language or repository topics.
    if labels["framework"] & {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP"}:
        labels["platform"].add("Windows")
    if labels["component"] & {"Win32", "COM", "WinRT", "Windows services", "Windows Registry"}:
        labels["platform"].add("Windows")
    purpose = "Application" if executable else "Unknown / library or tool"
    return {
        "platforms": sorted(labels["platform"]) or ["Unknown"],
        "os_targets": sorted(labels["platform"] & OS_TARGETS) or ["Unspecified"],
        "frameworks": sorted(labels["framework"]) or ["Unknown"],
        "purpose": purpose, "evidence": evidence[:200],
    }


def inspect_sources(source, executable, work):
    paths = sorted(path for path in source.rglob("*") if path.is_file())
    batches = []
    batch = []
    size = 0
    for path in paths:
        length = path.stat().st_size
        if batch and (len(batch) >= MAX_INSPECTOR_FILES or size + length > MAX_INSPECTOR_BYTES):
            batches.append(batch)
            batch = []
            size = 0
        batch.append(path)
        size += length
    if batch:
        batches.append(batch)
    if len(batches) <= 1:
        return inspect_source_batch(source, executable, work)
    components, frameworks = set(), set()
    evidence = []
    incomplete = Counter()
    for paths in batches:
        with tempfile.TemporaryDirectory(prefix="inspector-batch-", dir=work) as temporary:
            batch_work = Path(temporary)
            batch_source = batch_work / "source"
            for path in paths:
                destination = batch_source / path.relative_to(source)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
            result = inspect_source_batch(batch_source, executable, batch_work)
            components.update(result["components"])
            frameworks.update(result["frameworks"])
            evidence.extend(result["evidence"])
            incomplete.update(result["incomplete"])
    return {"components": sorted(components), "frameworks": sorted(frameworks),
            "evidence": evidence[:200], "incomplete": dict(incomplete)}


def inspect_source_batch(source, executable, work):
    rules = work / "rules.json"
    output = work / "inspector.json"
    rules.write_text(json.dumps(inspector_rules()), encoding="utf-8")
    command = [
        str(executable), "analyze", "-s", str(source), "-r", str(rules), "-i",
        "-f", "json", "-o", str(output), "-N", "-u", "-A",
        "--disable-archive-crawling", "--success-error-code-with-no-matches",
        "-p", "300000", "-F", "30000",
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=330)
    if result.returncode != 0:
        raise PilotError(f"Application Inspector exit {result.returncode}: {(result.stderr + result.stdout)[-1800:]}")
    report = json.loads(output.read_text(encoding="utf-8-sig"))
    metadata = report.get("metaData", {})
    matches = metadata.get("detailedMatchList")
    if not isinstance(matches, list):
        raise PilotError("Unexpected Application Inspector JSON schema: detailedMatchList missing")
    incomplete = {key: metadata.get(key, 0) for key in (
        "timedOut", "filesTimedOut", "filesTimeOutSkipped", "filesErrored", "filesSkipped",
    ) if metadata.get(key)}
    if incomplete:
        LOG.warning("Application Inspector incomplete: %s", json.dumps(incomplete))
    mapping = {f"PILOT_{key}": (kind, label) for key, kind, label, _ in RULES}
    components = set()
    frameworks = set()
    evidence = []
    for match in matches:
        if match["ruleId"] not in mapping:
            continue
        kind, label = mapping[match["ruleId"]]
        path = Path(match["fileName"]).resolve().relative_to(source.resolve()).as_posix()
        if kind == "component":
            components.add(label)
        else:
            frameworks.add(label)
        evidence.append({"rule": match["ruleId"], "kind": kind, "label": label,
                         "path": path, "line": match["startLocationLine"],
                         "engine": f"Application Inspector {INSPECTOR_VERSION}"})
    return {"components": sorted(components), "frameworks": sorted(frameworks),
            "evidence": evidence[:200], "incomplete": incomplete}


def application_types(frameworks, components):
    types = set(frameworks) & {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP"}
    cross = set(frameworks) & {"Electron", "Avalonia", ".NET MAUI", "Flutter", "Qt", "React Native"}
    types.update(f"Cross-platform: {name}" for name in cross)
    if "Windows services" in components:
        types.add("Windows service")
    if not types and "Win32" in components:
        types.add("Native / Win32 (UI not proven)")
    return sorted(types) or ["Console / other / unknown"]


def rest_repository_name(database_id):
    result = subprocess.run(["gh", "api", f"repositories/{int(database_id)}", "--jq", ".full_name"],
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    if re.search(r"404|Not Found|403|Repository access blocked|451", result.stderr):
        raise RepositoryUnavailable("Repository was deleted, made private, or blocked since the archived event")
    raise PilotError(f"Repository lookup failed: {result.stderr.strip()}")


def resolve_repository(candidate):
    """Fetch metadata, following renames/transfers via the archived numeric repository ID."""
    owner, name = candidate["name"].split("/", 1)
    repo = graphql(METADATA, allow_missing=True, owner=owner, name=name)["repository"]
    expected = candidate.get("database_id")
    if expected and (repo is None or repo["databaseId"] != expected):
        owner, name = rest_repository_name(expected).split("/", 1)
        repo = graphql(METADATA, allow_missing=True, owner=owner, name=name)["repository"]
        if repo is not None and repo["databaseId"] != expected:
            repo = None
    if repo is None or repo["isPrivate"]:
        raise RepositoryUnavailable("Repository is missing or no longer public")
    return repo


def analyze_repository(candidate, inspector, cache, semgrep=None):
    repo = resolve_repository(candidate)
    branch = repo["defaultBranchRef"]
    if not branch or not branch["target"].get("oid"):
        raise PilotError("Repository has no default-branch commit")
    sha = candidate.get("sha") or branch["target"]["oid"]
    scratch = ROOT / ".cache" / "work"
    if semgrep is not None:
        scratch.mkdir(parents=True, exist_ok=True)
    engine_config = semgrep_engine.identity(semgrep, scratch)
    key = hashlib.sha256(f"{repo['id']}:{sha}:{RULESET_VERSION}:{INSPECTOR_VERSION}:{json.dumps(engine_config, sort_keys=True)}".encode()).hexdigest()
    cached = cache / f"{key}.json"
    analysis = json.loads(cached.read_text(encoding="utf-8")) if cached.exists() else None
    if analysis and "ci" not in analysis:
        analysis = None
    if analysis and "container_base_images" not in analysis:
        analysis = None
    if analysis and "Windows" in analysis["platforms"] and analysis.get("inspector_strategy") != INSPECTOR_STRATEGY:
        analysis = None
    if analysis and semgrep is not None and analysis.get("semgrep", {}).get("status") != "success":
        analysis = None
    if analysis is None:
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="repo-pilot-", dir=scratch) as temporary:
            work = Path(temporary)
            source = work / "source"
            source.mkdir()
            files, skipped, source_method = acquire_sources(repo["nameWithOwner"], sha, source)
            container_images = base_images(files)
            ci_files = [item for item in files if is_ci_file(item[0])]
            files = [item for item in files if not is_ci_file(item[0])]
            for path, _ in ci_files:
                (source / path).unlink(missing_ok=True)
            analysis = classify(files)
            analysis["container_base_images"] = container_images
            analysis["ci"] = ci_signals(ci_files)
            analysis.update({"files_scanned": len(files), "excluded": skipped, "source_method": source_method,
                             "components": [], "application_types": [], "windows_scan": "not_applicable"})
            inspector_incomplete = {}
            project_inspector_evidence = []
            if "Windows" in analysis["platforms"]:
                result = inspect_sources(source, inspector, work)
                analysis["components"] = result["components"]
                analysis["frameworks"] = sorted((set(analysis["frameworks"]) - {"Unknown"}) | set(result["frameworks"])) or ["Unknown"]
                analysis["evidence"] = (result["evidence"] + analysis["evidence"])[:200]
                project_inspector_evidence = [item for item in result["evidence"] if item.get("label")]
                inspector_incomplete = result["incomplete"]
                analysis["windows_scan"] = "partial" if inspector_incomplete else "success"
            analysis["inspector_incomplete"] = inspector_incomplete
            supplemental = semgrep_engine.scan(source, semgrep, work, files)
            analysis["semgrep"] = {**supplemental, "configuration": engine_config}
            analysis["projects"] = classify_projects(files, classify, project_inspector_evidence + supplemental["evidence"])
            project_types = {label for project in analysis["projects"] for label in project["labels"]
                             if label.startswith(("PowerShell", "Cross-platform:"))
                             or label in {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP",
                                          "Windows service", "Service management"}}
            if "Windows" in analysis["platforms"]:
                # Inspector's broad service component includes management APIs.
                # Only project host evidence promotes it to an application type.
                type_components = [component for component in analysis["components"]
                                   if component != "Windows services" or "Windows service" in project_types]
                analysis["application_types"] = application_types(analysis["frameworks"], type_components)
            analysis["application_types"] = sorted(set(analysis["application_types"]) | project_types)
            analysis["inspector_strategy"] = INSPECTOR_STRATEGY
            analysis["status"] = "partial" if inspector_incomplete or any(skipped.get(k) for k in PARTIAL_REASONS) else "success"
            if not files and analysis["status"] == "success":
                analysis["status"] = "not_applicable"
                analysis["purpose"] = "No eligible source"
                analysis["note"] = "Repository inventory completed, but no in-scope source files were found; not a complete code scan."
            analysis["scanned_at"] = stamp(datetime.now(timezone.utc))
            cache.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(analysis), encoding="utf-8")
    return {
        **candidate, "id": repo["id"], "name": repo["nameWithOwner"], "url": repo["url"],
        "sha": sha, "fork": repo["isFork"], "archived": repo["isArchived"],
        "primary_language": (repo["primaryLanguage"] or {}).get("name", "Unknown"),
        "languages": {edge["node"]["name"]: edge["size"] for edge in repo["languages"]["edges"]},
        "languages_truncated": repo["languages"]["pageInfo"]["hasNextPage"],
        **analysis,
    }


def z_score(confidence):
    if confidence is None:
        return None
    if not 0.5 <= confidence < 1:
        raise ValueError("Confidence must be in [0.5, 1)")
    return NormalDist().inv_cdf(0.5 + confidence / 2)


def wilson(count, total, z):
    """Wilson score interval, as percentages; stays inside [0, 100] for small or extreme counts."""
    if not total or z is None:
        return None, None
    p = count / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return round(max(0.0, centre - half) * 100, 2), round(min(1.0, centre + half) * 100, 2)


def exclusive_percentages(counts, total):
    """Largest-remainder rounding to 0.01% so mutually exclusive shares display as exactly 100%."""
    units = 10000
    raw = {label: count * units / total for label, count in counts.items()}
    floors = {label: int(value) for label, value in raw.items()}
    remaining = units - sum(floors.values())
    for label in sorted(raw, key=lambda key: (floors[key] - raw[key], key))[:remaining]:
        floors[label] += 1
    return {label: value / 100 for label, value in floors.items()}


def distribution(records, field, labels=None, z=None, exclusive=False):
    counts = Counter()
    for record in records:
        values = record[field]
        counts.update(set(values if isinstance(values, list) else [values]))
    if labels:
        counts.update({label: 0 for label in labels})
    shares = exclusive_percentages(counts, len(records)) if exclusive and records else {}
    rows = []
    for label, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])):
        low, high = wilson(count, len(records), z)
        percent = shares.get(label, round(count / len(records) * 100, 2)) if records else None
        rows.append({"label": label, "count": count, "denominator": len(records),
                     "percent": percent, "ci_low": low, "ci_high": high})
    return rows


def language_platforms(records, z):
    """Primary-language distribution; each row carries that language's exclusive platform distribution."""
    rows = distribution(records, "primary_language", z=z, exclusive=True)
    for row in rows:
        members = [r for r in records if r["primary_language"] == row["label"]]
        counts = Counter(r["primary_platform"] for r in members)
        shares = exclusive_percentages(counts, len(members))
        row["platforms"] = [{"label": label, "count": count, "percent": shares[label]}
                            for label, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    return rows


def windows_ci_by_language(records, z):
    rows = []
    for row in distribution(records, "primary_language", z=z, exclusive=True):
        members = [r for r in records if r["primary_language"] == row["label"]]
        count = sum(bool((r.get("ci") or {}).get("windows")) for r in members)
        low, high = wilson(count, len(members), z)
        rows.append({"label": row["label"], "count": count, "denominator": len(members),
                     "percent": round(count / len(members) * 100, 2), "ci_low": low, "ci_high": high})
    return rows


def is_windows_candidate(record):
    review = record.get("cross_os") or {}
    cross_os = (review.get("status") == "success"
                and review.get("sha") == record.get("sha")
                and (review.get("decision") or {}).get("cross_os") is True)
    return record.get("status") == "success" and "Windows" in record.get("platforms", []) and not cross_os


def aggregate(records, confidence=None):
    z = z_score(confidence)
    for record in records:
        if "platforms" in record:
            record["primary_platform"] = primary_platform(record["platforms"])
            record["primary_framework"] = primary_framework(record["frameworks"])
    complete = [r for r in records if r["status"] == "success"]
    windows = [r for r in complete if is_windows_candidate(r)]
    applications = [r for r in windows if r["purpose"] == "Application" and r["windows_scan"] == "success"]
    project_labels = {
        "Windows Forms": "Windows Forms app",
        "WPF": "WPF app",
        "WinUI / Windows App SDK": "WinUI app",
        "UWP": "UWP app",
        "Windows service": "Windows service",
        "Service management": "Service management",
    }
    inventories = []
    unclassified = 0
    for record in complete:
        if not isinstance(record.get("projects"), list):
            continue
        labels = {label for project in record["projects"] for label in project.get("labels", [])}
        detected = {project_labels[label] for label in labels if label in project_labels}
        detected.update(labels & APPLICATION_TYPES)
        if "Executable" in labels:
            detected.add("Executable application")
        if labels & {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP"}:
            detected.add("Windows desktop app")
        if any(label.startswith("PowerShell") for label in labels):
            detected.add("PowerShell")
        detected.update(label for label in labels if label.startswith("Cross-platform:"))
        inventories.append({"project_types": sorted(detected)})
        if not detected:
            unclassified += 1
    return {
        "selected": len(records), "successful": len(complete),
        "partial": sum(r["status"] == "partial" for r in records),
        "failed": sum(r["status"] == "failed" for r in records),
        "not_applicable": sum(r["status"] == "not_applicable" for r in records),
        "windows_repositories": len(windows), "windows_applications": len(applications),
        "confidence_level": confidence,
        # Worst case (p = 50%) normal-approximation margin for the complete-scan denominator.
        "margin_of_error": round(z * (0.25 / len(complete)) ** 0.5 * 100, 2) if z and complete else None,
        "distribution_method": "exclusive-primary-1",
        "platforms": distribution(complete, "primary_platform", z=z, exclusive=True),
        "frameworks": distribution(complete, "primary_framework", z=z, exclusive=True),
        "languages": distribution(complete, "primary_language", z=z, exclusive=True),
        "language_platforms": language_platforms(complete, z),
        "windows_ci": windows_ci_by_language(complete, z),
        "application_types": distribution(applications, "application_types", z=z),
        "project_types": distribution(
            inventories, "project_types",
            [*project_labels.values(), "Windows desktop app", "PowerShell"],
            z=z,
        ),
        "project_types_unclassified": unclassified,
        "components": distribution(applications, "components", COMPONENTS, z=z),
        "candidate_components": distribution(windows, "components", COMPONENTS, z=z),
    }


GRAPHQL_ACTIVITY = ("Issue/PR openings, conversation comments, submitted PR reviews; last 20 comments/reviews per item. "
                    "Identified bots excluded; User accounts may still automate.")
ARCHIVE_ACTIVITY = ("Issue/PR opened or reopened, issue/PR conversation comments, submitted PR reviews, and inline "
                    "PR review comments from GH Archive. Logins matching bot patterns excluded; User accounts may "
                    "still automate.")


def default_archive_end(now=None):
    # GH Archive publishes each hour shortly after it closes; stay a few hours behind real time.
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=3)


def analyze_candidates(candidates, target, inspector, cache, skip_unavailable, semgrep=None):
    records, excluded = [], []
    for candidate in candidates:
        if len(records) >= target:
            break
        LOG.info("[%s/%s] %s", len(records) + 1, target, candidate["name"])
        try:
            record = (analyze_repository(candidate, inspector, cache, semgrep=semgrep) if semgrep is not None
                      else analyze_repository(candidate, inspector, cache))
        except RepositoryUnavailable as error:
            if skip_unavailable:
                # Ineligible at analysis time; replacing it keeps the sample uniform over eligible repositories.
                LOG.warning("%s: %s; drawing the next sampled repository", candidate["name"], error)
                excluded.append({"name": candidate["name"], "reason": str(error)})
                continue
            LOG.error("%s: %s", candidate["name"], error)
            record = {**candidate, "status": "failed", "error": str(error)}
        except (PilotError, urllib.error.URLError, TimeoutError, subprocess.TimeoutExpired,
                zipfile.BadZipFile, OSError, ValueError) as error:
            LOG.error("%s: %s", candidate["name"], error)
            record = {**candidate, "status": "failed", "error": str(error)}
        records.append(record)
    return records, excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100, help="Sample / cohort size (1-100)")
    parser.add_argument("--end", help="UTC window end on a whole hour, e.g. 2026-10-18T12:00:00Z")
    parser.add_argument("--discovery", choices=("auto", "gharchive", "graphql-search"), default="auto",
                        help="auto = GH Archive random sample, falling back to bounded GraphQL search")
    parser.add_argument("--seed", help="Sampling seed (default: window end timestamp)")
    parser.add_argument("--confidence", type=float, default=0.95, help="Confidence level for intervals (default 0.95)")
    parser.add_argument("--archive-workers", type=int, default=6)
    parser.add_argument("--archive-reserve", type=int, default=300,
                        help="Randomly ordered candidates drawn so unavailable repositories can be replaced")
    parser.add_argument("--archive-cache", type=Path, default=ROOT / ".cache" / "gharchive")
    parser.add_argument("--output", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--inspector", type=Path)
    parser.add_argument("--semgrep", type=Path, help="Optional local Semgrep executable; never installed automatically")
    parser.add_argument("--install-inspector", action="store_true")
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "analysis")
    parser.add_argument("--rerun-report", type=Path, help="Rescan a previous report's cohort and available pinned SHAs")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    if not 0.5 <= args.confidence < 1:
        parser.error("--confidence must be at least 0.5 and below 1")
    if args.archive_reserve < args.limit:
        parser.error("--archive-reserve must be at least --limit")
    if not shutil.which("gh"):
        parser.error("GitHub CLI is required; install it and run gh auth login")
    inspector = args.inspector
    if args.install_inspector:
        inspector = install_inspector(ROOT / ".tools" / "inspector")
    if inspector is None:
        matches = list((ROOT / ".tools" / "inspector").rglob("ApplicationInspector.CLI.exe"))
        inspector = matches[0] if len(matches) == 1 else None
    if not inspector or not inspector.is_file():
        parser.error("Application Inspector missing; use --install-inspector on Windows x64 or --inspector PATH")
    sampled = False
    if args.rerun_report:
        if args.end:
            parser.error("--end cannot be combined with --rerun-report")
        previous = json.loads(args.rerun_report.read_text(encoding="utf-8"))
        if previous["schema_version"] != 1:
            parser.error("Unsupported report schema")
        start, end = (parse_time(previous["window"][key]) for key in ("start", "end"))
        if end - start != timedelta(days=30):
            parser.error("Previous report must use a 30-day window")
        fields = {"name", "last_activity", "activity_types", "observed_events", "activity_evidence", "sha",
                  "database_id", "sample_rank", "sample_key"}
        candidates = [{key: value for key, value in record.items() if key in fields}
                      for record in previous["repositories"]]
        if not 1 <= len(candidates) <= 100:
            parser.error("Previous report must contain 1-100 repositories")
        coverage = {"mode": "bounded-graphql", "representative_sample": False, **previous["coverage"],
                    "rerun": True, "source_generated_at": previous["generated_at"]}
        target = len(candidates)
    else:
        coverage, candidates = {}, None
        if args.discovery in ("auto", "gharchive"):
            end = parse_time(args.end) if args.end else default_archive_end()
            start = end - timedelta(days=30)
            seed = args.seed or stamp(end)
            try:
                candidates, coverage = gharchive.discover(
                    start, end, seed, reserve=args.archive_reserve,
                    workers=args.archive_workers, cache_dir=args.archive_cache)
                coverage.update(mode="gharchive-random-sample", representative_sample=True,
                                activity=ARCHIVE_ACTIVITY)
                sampled = True
            except (gharchive.ArchiveUnavailable, ValueError) as error:
                if args.discovery == "gharchive":
                    raise PilotError(f"GH Archive discovery failed: {error}") from error
                LOG.warning("GH Archive unavailable (%s); falling back to bounded GraphQL search", error)
                coverage = {"fallback_reason": str(error)}
        if not sampled:
            end = parse_time(args.end) if args.end else datetime.now(timezone.utc)
            start = end - timedelta(days=30)
            candidates, search_coverage = discover(args.limit, start, end)
            coverage = {**coverage, **search_coverage, "mode": "bounded-graphql",
                        "representative_sample": False, "activity": GRAPHQL_ACTIVITY}
        coverage["requested_limit"] = args.limit
        target = args.limit
    if not candidates:
        raise PilotError("No qualifying repositories discovered; refusing to replace dashboard data")
    records, excluded = analyze_candidates(candidates, target, inspector.resolve(), args.cache,
                                          skip_unavailable=sampled, semgrep=args.semgrep)
    if sampled:
        coverage.update(excluded_after_sampling=excluded, sample_size=len(records),
                        candidates_drawn=len(records) + len(excluded))
        if len(records) < target:
            LOG.warning("Only %s eligible repositories in the reserve; sample is short of %s", len(records), target)
    confidence = args.confidence if coverage.get("representative_sample") else None
    report = {
        "schema_version": 1, "ruleset_version": RULESET_VERSION,
        "inspector_version": INSPECTOR_VERSION,
        "generated_at": stamp(datetime.now(timezone.utc)),
        "window": {"start": stamp(start), "end": stamp(end)},
        "coverage": coverage,
        "metrics": aggregate(records, confidence), "repositories": records,
    }
    from discovery.windows_container import analyze_report  # test branch only: workflow step cannot be pushed
    analyze_report(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending = args.output.with_suffix(".tmp")
    pending.write_text(json.dumps(report, indent=2), encoding="utf-8")
    pending.replace(args.output)
    LOG.info("Wrote %s; metrics: %s", args.output, json.dumps(report["metrics"])[:500])
    if not report["metrics"]["successful"]:
        raise PilotError("No complete scans; report saved for diagnostics, workflow must not deploy it")


if __name__ == "__main__":
    try:
        main()
    except (PilotError, urllib.error.URLError, subprocess.TimeoutExpired) as error:
        LOG.error("%s", error)
        raise SystemExit(1) from error
