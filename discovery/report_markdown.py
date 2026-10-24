"""Publish a GitHub-readable report and SVG charts from the collected JSON."""

import argparse
from html import escape
import json
from pathlib import Path
import re

from discovery.report_pdf import EXCLUSIVE, ROOT, SECTIONS, number, unknown_project_platform_rows


def text(value):
    if isinstance(value, list):
        value = ", ".join(map(str, value))
    value = escape("" if value is None else str(value), quote=True)
    value = re.sub(r"([\\`*_{}\[\]()!|~])", r"\\\1", value)
    return " ".join(value.splitlines())


def chart_svg(rows, title):
    rows = rows or []
    height = 60 + max(1, len(rows)) * 44
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" '
        f'viewBox="0 0 1000 {height}" role="img">',
        f"<title>{escape(title)}</title>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<g font-family="sans-serif" font-size="14" fill="#17202a">'
        f'<text x="16" y="28">{escape(title)}</text>',
    ]
    if not rows or all(row["denominator"] == 0 for row in rows):
        parts.append('<text x="16" y="70">N/A — no eligible repositories.</text>')
    else:
        for index, row in enumerate(rows):
            y = 60 + index * 44
            percent = row["percent"]
            width = max(0, min(100, percent or 0)) * 4
            parts.extend([
                f'<text x="16" y="{y}">{escape(str(row["label"]))}</text>',
                f'<rect x="480" y="{y - 14}" width="400" height="18" fill="#e6ebf2"/>',
                f'<rect x="480" y="{y - 14}" width="{width}" height="18" fill="#2f6fdd"/>',
                f'<text x="890" y="{y}">{escape(number(percent, "%"))}</text>',
            ])
    return "".join(parts) + "</g></svg>\n"


def build_markdown(report):
    metrics, coverage = report["metrics"], report["coverage"]
    confidence = metrics.get("confidence_level") if coverage.get("representative_sample") else None
    lines = [
        "# Windows app discovery — latest report", "",
        f"Activity window (UTC): {text(report['window']['start'])} → {text(report['window']['end'])}",
        f"Generated: {text(report['generated_at'])}  ",
        f"Ruleset: {text(report['ruleset_version'])}; Application Inspector: {text(report['inspector_version'])}", "",
    ]
    if coverage.get("representative_sample"):
        lines.extend([
            f"Uniform random sample from {text(coverage.get('population_size'))} public repositories "
            "with qualifying human activity.",
            f"Seed: {text(coverage.get('seed'))}; archive hours: {text(coverage.get('hours_processed'))}/"
            f"{text(coverage.get('hours_expected'))}; qualifying events: {text(coverage.get('qualifying_events'))}; "
            f"deleted/private replacements: {len(coverage.get('excluded_after_sampling', []))}.",
        ])
        if confidence:
            lines.append(f"{round(confidence * 100)}% Wilson confidence intervals; worst-case margin for complete "
                         f"scans: ±{text(number(metrics.get('margin_of_error')))} percentage points.")
    else:
        lines.append("**Bounded, non-representative GraphQL cohort.** Percentages describe the analyzed cohort "
                     "only; no confidence intervals are reported.")
        if coverage.get("fallback_reason"):
            lines.append(f"Fallback reason: {text(coverage['fallback_reason'])}")
    lines.extend(["", "| Metric | Repositories |", "| --- | ---: |"])
    for label, key in (("Sampled", "selected"), ("Complete scans", "successful"), ("Partial", "partial"),
                       ("Failed", "failed"), ("No eligible source", "not_applicable"),
                       ("Windows candidates (subset of complete scans)", "windows_repositories"),
                       ("Windows applications (subset of complete scans)", "windows_applications")):
        lines.append(f"| {label} | {text(metrics.get(key, 0))} |")
    for key, title, note in SECTIONS:
        lines.extend(["", f"## {title}", "", note, ""])
        if key in EXCLUSIVE:
            lines.extend([f"Each repository belongs to one category; shares total 100% across the "
                          f"{metrics['successful']} complete scans only. Partial, failed, and no-eligible-source "
                          "repositories are excluded.", ""])
        lines.extend([f"![{title}]({key}.svg)", ""])
        if key == "project_types" and key not in metrics:
            lines.append("Not collected by this report; rerun the collector to populate project findings.")
            continue
        rows = metrics.get(key) or []
        if not rows or all(row["denominator"] == 0 for row in rows):
            lines.append("N/A — no eligible repositories.")
            continue
        lines.extend(["| Category | Count / denominator | Share |" + (" CI |" if confidence else ""),
                      "| --- | ---: | ---: |" + (" --- |" if confidence else "")])
        for row in rows:
            interval = (f" {text(number(row.get('ci_low')))}–"
                        f"{text(number(row.get('ci_high'), '%'))} |") if confidence else ""
            lines.append(f"| {text(row['label'])} | {row['count']} / {row['denominator']} | "
                         f"{text(number(row['percent'], '%'))} |{interval}")
        if key == "project_types" and "unknown_project_platforms" in metrics:
            unknown_rows = unknown_project_platform_rows(metrics["unknown_project_platforms"])
            if unknown_rows:
                lines.extend(["", "### Unknown / no findings by primary platform", "",
                              "Platforms above 30% are listed separately; the rest are grouped as Others.", "",
                              "| Platform | Count / denominator | Share |",
                              "| --- | ---: | ---: |"])
                for row in unknown_rows:
                    lines.append(f"| {text(row['label'])} | {row['count']} / {row['denominator']} | "
                                 f"{text(number(row['percent'], '%'))} |")
    lines.extend(["", "## Sampled repositories", "",
                  "| Repository | Scan | Language | Platform | Framework | Windows app types | Components |",
                  "| --- | --- | --- | --- | --- | --- | --- |"])
    for repository in report["repositories"]:
        lines.append("| " + " | ".join(text(repository.get(key)) for key in (
            "name", "status", "primary_language", "primary_platform", "primary_framework",
            "application_types", "components")) + " |")
    lines.extend(["", "Static source-level evidence is not proof of runtime use or OS compatibility. "
                  "Component and application-type categories can overlap. Partial and failed scans are "
                  "nonresponse; their exclusion can bias estimates. Sampling intervals do not measure "
                  "classification error or nonresponse bias.",
                  "", "See the [methodology and full metric definitions](../README.md#metric-definitions).", ""])
    return "\n".join(lines)


def write_report(report, output):
    if not report["metrics"]["successful"]:
        raise ValueError("Cannot publish a report with no complete scans")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for key, title, _ in SECTIONS:
        (output / f"{key}.svg").write_text(chart_svg(report["metrics"].get(key), title), encoding="utf-8")
    (output / "README.md").write_text(build_markdown(report), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    write_report(json.loads(args.input.read_text(encoding="utf-8")), args.output)


if __name__ == "__main__":
    main()
