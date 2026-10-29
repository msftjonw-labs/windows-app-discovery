"""Classify clearly documented application OS support from pinned GitHub evidence."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import logging
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import quote
import urllib.error

from discovery.pilot import ROOT, PilotError, fetch_source_batch, safe_path, stamp
from discovery.rules import EXCLUDED_DIRS

LOG = logging.getLogger("cross_os")
VERSION = "cross-os-4"
MAX_DOCUMENTS = 100
MAX_FILE_BYTES = 1024 * 1024
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_CHARS = 96000
OS_NAMES = ("Windows", "Linux", "macOS", "Android", "iOS", "FreeBSD", "OpenBSD", "NetBSD", "ChromeOS")
OS_PATTERN = re.compile(
    r"\b(?:windows|win32|win64|linux|ubuntu|debian|macos|mac\s+os|darwin|"
    r"android|ios|freebsd|openbsd|netbsd|chromeos|cross[- ]platform|operating systems?)\b", re.I)
METHOD = (
    "Deterministic review of pinned public GitHub documentation; no OpenAI API is used. "
    "Cross-OS requires explicit documentation of application support for at least two operating systems. "
    "CI runners, languages, frameworks, browser access, and inferred portability do not qualify. "
    "All other sampled repositories are non-cross-OS: support not demonstrated, not proven "
    "OS-specificity or incompatibility. Both categories use the full sample denominator, including "
    "ambiguous and undocumented repositories. Static evidence review, not cross-OS runtime testing."
)
SUPPORT_MARKER = re.compile(
    r"\b(?:support(?:s|ed)?|available|download(?:s)?|release(?:s|d)?|compatible|runs?\s+on)\b",
    re.I,
)
OS_PATTERNS = {
    "Windows": re.compile(r"\b(?:windows|win32|win64)\b", re.I),
    "Linux": re.compile(r"\blinux\b", re.I),
    "macOS": re.compile(r"\b(?:macos|mac\s+os(?:\s+x)?|darwin|os\s+x)\b", re.I),
    "Android": re.compile(r"\bandroid\b", re.I),
    "iOS": re.compile(r"\bios\b", re.I),
    "FreeBSD": re.compile(r"\bfreebsd\b", re.I),
    "OpenBSD": re.compile(r"\bopenbsd\b", re.I),
    "NetBSD": re.compile(r"\bnetbsd\b", re.I),
    "ChromeOS": re.compile(r"\bchrome\s*os\b", re.I),
}
NON_APPLICATION_CONTEXT = re.compile(
    r"\b(?:ci|workflow|runner|lint|documentation|docs|test suite|unit tests?|"
    r"development environment|build host|docker desktop|wsl)\b", re.I,
)
UNCERTAIN_OR_NEGATED = re.compile(
    r"\b(?:may|might|could|possibly|potentially|planned|plan to|"
    r"does not|do not|doesn't|don't|not yet|unsupported|not supported)\b", re.I,
)
def eligible_document(path):
    path = PurePosixPath(str(path).lower())
    excluded = (EXCLUDED_DIRS - {"docs", "doc", "documentation"}) | {
        "external", "third-party", ".agents", ".agent", ".claude", "code-review-artifacts",
        "__fuzz__", "corpus"}
    if any(part in excluded for part in path.parts[:-1]) and not (
            len(path.parts) == 3 and path.parts[:2] == (".github", "workflows")):
        return False
    if path.suffix not in {"", ".md", ".mdx", ".rst", ".txt", ".json", ".toml", ".yaml", ".yml",
                           ".csproj", ".fsproj", ".vbproj", ".kts", ".gradle", ".sh", ".ps1"}:
        return False
    name = path.name
    if not path.suffix and not (name.startswith("readme") or name in {"install", "installation", "makefile"}):
        return False
    return (
        name.startswith(("readme", "install"))
        or path.parts[:2] == (".github", "workflows")
        or name in {"package.json", "cargo.toml", "pyproject.toml", "pubspec.yaml", "cmakelists.txt",
                    "makefile", ".goreleaser.yaml", ".goreleaser.yml", ".travis.yml",
                    "appveyor.yml", ".gitlab-ci.yml", "azure-pipelines.yml",
                    "build.gradle", "build.gradle.kts", "tauri.conf.json"}
        or path.suffix in {".csproj", ".fsproj", ".vbproj"}
        or bool(re.search(r"(?:support|platform|deploy|install|build|requirements|quick.?start|getting.?started|releas|compatib)",
                          str(path)))
    )


def github_json(endpoint):
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True,
                            encoding="utf-8", timeout=120)
    if result.returncode:
        raise PilotError("Cross-OS evidence request failed: " + result.stderr.strip())
    return json.loads(result.stdout)


def collect_evidence(repository):
    name, sha = repository["name"], repository["sha"]
    if github_json(f"repos/{name}")["private"]:
        raise PilotError("Cross-OS analysis requires a currently public repository")
    tree = github_json(f"repos/{name}/git/trees/{sha}?recursive=1")
    limits = []
    if tree["truncated"]:
        limits.append("GitHub source tree truncated")
    candidates = []
    for entry in tree["tree"]:
        if entry["type"] != "blob" or entry.get("mode") in {"120000", "160000"}:
            continue
        if not isinstance(entry.get("path"), str):
            raise PilotError("Invalid cross-OS evidence path")
        path = PurePosixPath(entry["path"])
        if not eligible_document(path):
            continue
        path = safe_path(entry["path"])
        size = entry["size"]
        if not isinstance(size, int) or size < 0:
            raise PilotError(f"Invalid evidence file size: {path}")
        if size > MAX_FILE_BYTES:
            limits.append(f"Oversize evidence file omitted: {path}")
            continue
        candidates.append((path, size, entry["sha"]))
    candidates.sort(key=lambda item: (
        0 if len(item[0].parts) == 1 and item[0].name.lower().startswith("readme") else
        2 if item[0].parts[:2] == (".github", "workflows") else 1,
        len(item[0].parts), str(item[0])))
    selected, size = [], 0
    for entry in candidates:
        if len(selected) >= MAX_DOCUMENTS or size + entry[1] > MAX_SOURCE_BYTES:
            limits.append("Document count or source byte bound reached")
            break
        selected.append(entry)
        size += entry[1]
    sources, evidence_size = [], 0
    for offset in range(0, len(selected), 40):
        batch = selected[offset:offset + 40]
        contents = fetch_source_batch(name, sha, batch)
        if len(contents) != len(batch):
            raise PilotError("Incomplete cross-OS evidence response")
        for (path, _, _), raw in zip(batch, contents):
            if raw is None:
                raise PilotError(f"Cross-OS evidence file unavailable: {path}")
            try:
                content = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                limitation = f"Non-UTF-8 evidence file omitted: {path}"
                LOG.warning("%s: %s", name, limitation)
                limits.append(limitation)
                continue
            if any(ord(char) < 32 and char not in "\t\n\r" for char in content):
                limitation = f"Binary evidence file omitted: {path}"
                LOG.warning("%s: %s", name, limitation)
                limits.append(limitation)
                continue
            lines = content.splitlines()
            wanted = set(range(min(20, len(lines))))
            for index, line in enumerate(lines):
                if OS_PATTERN.search(line):
                    wanted.update(range(max(0, index - 3), min(len(lines), index + 5)))
            excerpt, length = [], 0
            for index in sorted(wanted):
                line = lines[index]
                if length + len(line) > 8000 or evidence_size + len(line) > MAX_EVIDENCE_CHARS:
                    limits.append(f"Evidence excerpt bounded: {path}")
                    break
                excerpt.append({"line": index + 1, "text": line})
                length += len(line)
                evidence_size += len(line)
            if excerpt:
                sources.append({
                    "id": f"S{len(sources) + 1}", "path": str(path),
                    "url": f"https://github.com/{name}/blob/{sha}/{quote(str(path))}",
                    "lines": excerpt,
                })
    return {"repository": name, "sha": sha, "sources": sources, "limitations": sorted(set(limits))}


def classify(evidence):
    for source in evidence["sources"]:
        path = source["path"].lower()
        if path.startswith(".github/workflows/") or path.endswith((".sh", ".ps1")):
            continue
        for line in source["lines"]:
            value = line["text"]
            if (not SUPPORT_MARKER.search(value) or NON_APPLICATION_CONTEXT.search(value)
                    or UNCERTAIN_OR_NEGATED.search(value)):
                continue
            systems = [name for name, pattern in OS_PATTERNS.items() if pattern.search(value)]
            if len(systems) >= 2:
                references = [
                    {"os": system, "source_id": source["id"], "first_line": line["line"],
                     "last_line": line["line"], "quote": value}
                    for system in systems
                ]
                decision = {
                    "cross_os": True, "application": "Repository application",
                    "rationale": "A repository application document explicitly lists support for multiple operating systems.",
                    "support": references,
                }
                validate_decision(decision, [source])
                return {"decision": decision, "sources": [{**source, "lines": [line]}]}
    return {"decision": {
        "cross_os": False, "application": "", "support": [],
        "rationale": "Explicit multi-OS application support not demonstrated in the reviewed evidence.",
    }, "sources": []}


def source_quote(citation, ids):
    source_id = citation["source_id"]
    if citation["os"] not in OS_NAMES or not isinstance(source_id, str) or source_id not in ids:
        raise PilotError("Unknown cross-OS support OS or source")
    first, last = citation["first_line"], citation["last_line"]
    if type(first) is not int or type(last) is not int or first < 1 or first != last:
        raise PilotError("Invalid cross-OS citation line range")
    lines = {line["line"]: line["text"] for line in ids[source_id]["lines"]}
    if any(index not in lines for index in range(first, last + 1)):
        raise PilotError("Cross-OS citation references omitted lines")
    quote = "\n".join(lines[index] for index in range(first, last + 1))
    if not quote.strip():
        raise PilotError("Cross-OS support citation is empty")
    return quote


def validate_decision(decision, sources):
    if not isinstance(decision, dict) or set(decision) != {"cross_os", "application", "rationale", "support"}:
        raise PilotError("Invalid cross-OS decision shape")
    if (type(decision["cross_os"]) is not bool
            or not isinstance(decision["application"], str)
            or not isinstance(decision["rationale"], str) or not decision["rationale"].strip()
            or not isinstance(decision["support"], list)):
        raise PilotError("Invalid cross-OS decision values")
    ids = {source["id"]: source for source in sources}
    systems = set()
    for citation in decision["support"]:
        if not isinstance(citation, dict) or set(citation) != {
                "os", "source_id", "first_line", "last_line", "quote"}:
            raise PilotError("Invalid cross-OS support citation")
        if citation["quote"] != source_quote(citation, ids):
            raise PilotError("Cross-OS support quote does not match pinned source")
        systems.add(citation["os"])
    if decision["cross_os"]:
        if not decision["application"].strip() or len(systems) < 2:
            raise PilotError("Cross-OS application requires cited support for at least two OSes")
    elif decision["support"] or decision["application"]:
        raise PilotError("Non-cross-OS decision must not assert application OS support")


def enrich(report):
    for repository in report["repositories"]:
        assessment = {"version": VERSION, "sha": repository.get("sha"),
                      "generated_at": stamp(datetime.now(timezone.utc))}
        try:
            if not repository.get("sha"):
                assessment.update(status="success", **classify({"sources": []}),
                                  documents_reviewed=0, limitations=["No pinned commit available"])
                repository["cross_os"] = assessment
                continue
            LOG.info("Checking pinned GitHub evidence: %s", repository["name"])
            evidence = collect_evidence(repository)
            result = classify(evidence)
            assessment.update(status="success", **result,
                              documents_reviewed=len(evidence["sources"]),
                              limitations=evidence["limitations"])
        except (PilotError, urllib.error.URLError, TimeoutError, subprocess.TimeoutExpired,
                OSError, ValueError, KeyError, TypeError) as error:
            LOG.error("%s: GitHub evidence review failed: %s", repository["name"], error)
            assessment.update(status="failed", error=str(error))
        repository["cross_os"] = assessment
    report["metrics"]["cross_os"] = summary(report)
    return report


def summary(report):
    repositories = report["repositories"]
    groups = {True: [], False: []}
    failures, missing, ambiguous = [], [], []
    for repository in repositories:
        result = repository.get("cross_os")
        if not result:
            missing.append(repository["name"])
        elif result.get("status") == "ambiguous" and result.get("sha") == repository.get("sha"):
            ambiguous.append(repository["name"])
            groups[False].append(repository)
        elif result.get("status") != "success" or result.get("sha") != repository.get("sha"):
            failures.append(repository["name"])
        else:
            decision = result["decision"]
            validate_decision(decision, result["sources"])
            groups[decision["cross_os"]].append(repository)
    total = len(repositories)
    denominator = sum(map(len, groups.values()))
    complete = total > 0 and not failures and not missing
    rows = []
    if complete:
        for positive, members in groups.items():
            languages = Counter(r.get("primary_language", "Unknown") for r in members)
            ranked = sorted(languages.items(), key=lambda item: (-item[1], item[0]))
            ranks = sorted(set(languages.values()), reverse=True)[:2]
            top = [[{"language": language, "count": count, "percent": round(count / len(members) * 100, 2)}
                    for language, count in ranked if count == rank] for rank in ranks] if members else []
            rows.append({
                "label": "Cross-OS" if positive else "Non-cross-OS",
                "count": len(members), "denominator": denominator,
                "percent": round(len(members) / denominator * 100, 2) if denominator else 0,
                "top_languages": top,
            })
    return {"complete": complete, "selected": total, "assessed": denominator,
            "ambiguous": ambiguous, "skipped": 0,
            "failed": failures, "missing": missing, "rows": rows, "method": METHOD}


def write_assessments(report, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": 1, "generated_at": report["generated_at"], "window": report["window"],
        "summary": summary(report),
        "repositories": [
            {key: repository[key] for key in ("name", "sha", "primary_language", "cross_os")
             if key in repository}
            for repository in report["repositories"]
        ],
    }
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--assessments-output", type=Path,
                        help="Also export the per-repository review evidence and language summary")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = json.loads(args.report.read_text(encoding="utf-8"))
    if report.get("schema_version") != 1 or not isinstance(report.get("repositories"), list):
        parser.error("Unsupported report schema")
    enrich(report)
    pending = args.report.with_suffix(".tmp")
    pending.write_text(json.dumps(report, indent=2), encoding="utf-8")
    pending.replace(args.report)
    if args.assessments_output:
        write_assessments(report, args.assessments_output)
    if not report["metrics"]["cross_os"]["complete"]:
        raise SystemExit("GitHub evidence collection incomplete; diagnostics saved and distribution withheld.")


if __name__ == "__main__":
    main()
