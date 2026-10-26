"""Assess Windows-container evidence from the already scanned repository sources."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]

WINDOWS_IMAGE = re.compile(
    r"(?:^|[/_.:-])(?:windows(?:servercore)?|nanoserver|servercore)(?:[/_.:-]|$)|ltsc20\d{2}",
    re.I,
)
LINUX_IMAGE = re.compile(
    r"(?:^|[/:._-])(?:alpine[\d.]*|amazonlinux|busybox|centos|debian|fedora|opensuse|rockylinux|ubuntu|distroless"
    r"|slim|bookworm|bullseye|buster|trixie|bionic|focal|jammy|noble|ol\d+)(?=[/:@._-]|$)|^scratch$",
    re.I,
)
CONTAINER_LABEL = "Container / orchestration configuration"
GUI_LABELS = {"Windows Forms", "Windows Forms app", "WPF", "WPF app", "WinUI / Windows App SDK",
              "WinUI app", "UWP", "UWP app", "Native desktop app", "Windows desktop app",
              "Cross-platform: Electron", "Cross-platform: Flutter", "Cross-platform: Qt",
              "Cross-platform: Avalonia", "Cross-platform: .NET MAUI", "Cross-platform: React Native"}
RUNNABLE_LABELS = {"Backend / API", "Command-line tool", "Executable application", "Windows service"}
CONDITIONAL_COMPONENTS = {"COM", "WinRT", "Windows Registry", "Windows services", ".NET native interop"}
POOR_FIT_COMPONENTS = {"DirectX"}


def base_images(files):
    findings = []
    for path, content in files:
        name = PurePosixPath(path).name.lower()
        if name != "containerfile" and not name.startswith("dockerfile"):
            continue
        for number, line in enumerate(content.splitlines(), 1):
            match = re.match(r"^\s*FROM\s+(.+?)\s*$", line, re.I)
            if not match:
                continue
            tokens = match.group(1).split()
            while tokens and tokens[0].startswith("--"):
                option = tokens.pop(0)
                if option == "--platform" and tokens:
                    tokens.pop(0)
            if tokens:
                findings.append({"path": path, "line": number, "image": tokens[0]})
    return findings


def classify(record):
    scan_status = record.get("status")
    if scan_status != "success":
        return {
            "status": "incomplete_scan",
            "summary": "Source scan incomplete; container compatibility was not assessed.",
            "evidence": [],
        }

    images = record.get("container_base_images", [])
    if not images:
        return {
            "status": "no_container_image_evidence",
            "summary": "No Dockerfile or Containerfile base image was found in the scanned source; this does not establish incompatibility.",
            "evidence": [],
        }

    kinds = set()
    evidence = []
    for image in images:
        reference = image["image"]
        kind = "windows" if WINDOWS_IMAGE.search(reference) else (
            "linux" if LINUX_IMAGE.search(reference) else "unknown"
        )
        kinds.add(kind)
        evidence.append({**image, "image_os": kind})

    if kinds == {"windows"}:
        status = "windows_base_image"
        summary = "Explicit Windows container base image configured; build and runtime compatibility were not tested."
    elif kinds == {"linux"}:
        status = "linux_base_image"
        summary = "Explicit Linux container base image configured; Windows-container compatibility is not established."
    else:
        status = "ambiguous_or_mixed_images"
        summary = "Container base-image evidence is mixed or ambiguous; Windows-container compatibility is undetermined."
    return {"status": status, "summary": summary, "evidence": evidence}


def containerization_candidate(record):
    if record.get("status") != "success":
        return {"status": "incomplete_scan", "summary": "Source scan incomplete; suitability was not assessed.",
                "evidence": []}
    if "Windows" not in record.get("platforms", []):
        return {"status": "not_windows_targeted", "summary": "No Windows target was detected.",
                "evidence": []}

    projects = record.get("projects", [])
    labels = {label for project in projects for label in project.get("labels", [])}
    components = set(record.get("components", []))
    if record.get("container_base_images") or CONTAINER_LABEL in labels:
        return {"status": "already_containerized",
                "summary": "Container or orchestration configuration was detected; excluded from the not-yet-containerized assessment.",
                "evidence": []}

    evidence = []
    for project in projects:
        for item in project.get("evidence", []):
            if item.get("label") in labels:
                evidence.append({
                    "label": item["label"], "path": item.get("path", project.get("path", ".")),
                    "line": item.get("line"),
                })
    for item in record.get("evidence", []):
        if item.get("label") in components:
            evidence.append({
                "label": item["label"], "path": item.get("path", "."),
                "line": item.get("line"),
            })
    evidence = sorted({(item["label"], item["path"], item["line"]) for item in evidence})
    cues = labels | components

    gui = sorted(cues & GUI_LABELS)
    if gui or components & POOR_FIT_COMPONENTS:
        status = "poor_fit"
        reasons = gui or sorted(components & POOR_FIT_COMPONENTS)
        summary = ("Detected desktop UI or graphics dependency is a poor fit for standard Windows Server containers: "
                   + ", ".join(reasons) + ".")
    else:
        runnable = sorted(cues & RUNNABLE_LABELS)
        conditional = sorted((cues & CONDITIONAL_COMPONENTS) | {
            label for label in cues if label.startswith("Cross-platform:")
        })
        if runnable and not conditional:
            status = "potentially_suitable"
            summary = ("Runnable application type detected (" + ", ".join(runnable)
                       + "); a Windows-container build and runtime test is still required.")
        elif runnable or conditional:
            status = "conditional"
            reasons = sorted(set(runnable + conditional))
            summary = ("Containerization may be possible, but detected Windows/cross-platform dependencies or "
                       "application type need validation: " + ", ".join(reasons) + ".")
        else:
            status = "insufficient_evidence"
            summary = ("No clear runnable application type was detected; source evidence is insufficient to judge "
                       "whether this project is a suitable container workload.")
    return {
        "status": status, "summary": summary,
        "evidence": [{"label": label, "path": path, "line": line} for label, path, line in evidence],
    }


def analyze_report(report):
    counts = {
        "windows_base_image": 0,
        "linux_base_image": 0,
        "ambiguous_or_mixed_images": 0,
        "no_container_image_evidence": 0,
        "incomplete_scan": 0,
    }
    assessed = 0
    candidate_counts = {
        "potentially_suitable": 0,
        "conditional": 0,
        "poor_fit": 0,
        "insufficient_evidence": 0,
        "already_containerized": 0,
        "not_windows_targeted": 0,
        "incomplete_scan": 0,
    }
    for record in report.get("repositories", []):
        result = classify(record)
        record["windows_container"] = result
        counts[result["status"]] += 1
        if result["status"] != "incomplete_scan":
            assessed += 1
        candidate = containerization_candidate(record)
        record["windows_container_candidate"] = candidate
        candidate_counts[candidate["status"]] += 1
    report.setdefault("metrics", {})["windows_container_compatibility"] = {
        "assessed": assessed,
        "counts": counts,
        "containerization_candidates": candidate_counts,
        "method": "Static base-image indicators from scanned Dockerfiles and Containerfiles; no build or runtime test.",
        "candidate_method": (
            "Among complete Windows-targeted scans, repositories with container/orchestration configuration or "
            "Dockerfile/Containerfile base images are excluded. Remaining project-type and Windows-component "
            "indicators are heuristic screening evidence, not a test of Windows-container support."
        ),
    }
    return report


def report_rows(report):
    compatibility = report["metrics"]["windows_container_compatibility"]
    summary = [
        ("Base-image evidence", label, compatibility["counts"].get(key, 0))
        for key, label in (
            ("windows_base_image", "Windows base image configured"),
            ("linux_base_image", "Linux base image configured"),
            ("ambiguous_or_mixed_images", "Mixed or ambiguous base images"),
            ("no_container_image_evidence", "No container base-image evidence"),
            ("incomplete_scan", "Incomplete source scan"),
        )
    ]
    candidates = compatibility.get("containerization_candidates")
    if candidates:
        summary.extend(
            ("Containerization potential", label, candidates.get(key, 0))
            for key, label in (
                ("potentially_suitable", "Potentially suitable; validate with a build/run"),
                ("conditional", "Conditional; dependencies or project type need review"),
                ("poor_fit", "Poor fit for standard Windows Server containers"),
                ("insufficient_evidence", "Insufficient project evidence"),
                ("already_containerized", "Excluded: container/orchestration evidence detected"),
                ("not_windows_targeted", "Excluded: no Windows target detected"),
                ("incomplete_scan", "Not assessed: incomplete scan"),
            )
        )
    repositories = []
    for repository in report["repositories"]:
        existing = repository.get("windows_container", {})
        candidate = repository.get("windows_container_candidate", {})
        if not existing.get("evidence") and candidate.get("status") not in {
            "potentially_suitable", "conditional", "poor_fit", "insufficient_evidence", "already_containerized",
        }:
            continue
        evidence = [
            f"{item['image']} ({item['image_os']}; {item['path']}:{item['line']})"
            for item in existing.get("evidence", [])
        ]
        evidence.extend(
            f"{item['label']} ({item['path']}{':' + str(item['line']) if item.get('line') else ''})"
            for item in candidate.get("evidence", [])
        )
        repositories.append((
            repository,
            existing.get("summary", "Base-image analysis not collected."),
            candidate.get("summary", "Suitability analysis not collected."),
            ", ".join(evidence) or "No specific project evidence",
        ))
    return summary, repositories


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "site" / "data" / "latest.json")
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    analyze_report(report)
    pending = args.report.with_suffix(".tmp")
    pending.write_text(json.dumps(report, indent=2), encoding="utf-8")
    pending.replace(args.report)


if __name__ == "__main__":
    main()
