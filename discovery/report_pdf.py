"""Render site/data/latest.json as a print-friendly PDF with headless Chrome/Edge.

Run with: python -m discovery.report_pdf --input site/data/latest.json --output site/report.pdf
"""

import argparse
from datetime import datetime, timezone
from html import escape
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from discovery.windows_container import report_rows
from discovery.cross_os import summary as cross_os_summary
from discovery.pilot import is_windows_candidate

ROOT = Path(__file__).resolve().parents[1]
BROWSERS = (
    os.environ.get("PDF_BROWSER", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
)
SECTIONS = (
    ("language_platforms", "Primary programming languages and their target platforms",
     "GitHub's primary language per repository. The last column splits each language's repositories by primary target "
     "platform (an explicit OS target wins, several OS targets = Multiple OS, otherwise the most specific environment; "
     "generic runtimes/scripts come last), so each language's platform shares add up to 100%."),
    ("frameworks", "Framework evidence", "Most specific detected framework per repository (e.g. Next.js before React)."),
    ("project_types", "Project application and automation types",
     "Share of complete repository scans with collected project findings, including libraries/tools and non-Windows "
     "PowerShell. Each repository counts once per category across its projects. Categories overlap: Windows desktop "
     "app includes Windows Forms, WPF, WinUI, and UWP; shares need not sum to 100%. Older inventories without project "
     "findings are excluded. Types are identified from source patterns and project metadata, not inferred from OS "
     "or language. Repositories without sufficient type evidence remain in the denominator and are reported in "
     "the classification coverage note, not as application types. Static indicators do not prove executable or runtime behavior."),
    ("application_types", "Windows application types", "Complete Windows application scans; types can overlap."),
    ("components", "Windows component adoption", "Complete Windows application scans; components overlap."),
    ("windows_ci", "Windows CI by primary language",
     "Complete scans whose CI configuration (GitHub Actions, AppVeyor, Azure Pipelines, GitLab CI, CircleCI) "
     "references a Windows runner or GOOS=windows. Shows intent to build/test on Windows, not run results; "
     "dynamic matrices and external CI are not detected. Not an application metric."),
    ("candidate_components", "Exploratory: all Windows candidates", "Includes libraries/tools; not an application metric."),
)
EXCLUSIVE = {"language_platforms", "frameworks"}
CSS = """
@page { size: Letter; margin: 14mm 12mm; }
@page windows-repositories { size: Letter landscape; margin: 14mm 12mm; }
body { font: 10pt/1.4 "Segoe UI", Arial, sans-serif; color: #17202a; }
h1 { font-size: 18pt; margin: 0 0 4px; } h2 { font-size: 13pt; margin: 18px 0 6px; border-bottom: 1px solid #ccd; }
.muted { color: #5b6773; } .notice { background: #f3f6fb; border-left: 4px solid #2f6fdd; padding: 6px 10px; }
.cards { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.card { border: 1px solid #ccd; border-radius: 4px; padding: 4px 8px; min-width: 88px; }
.card strong { display: block; font-size: 14pt; }
.card.subset { background: #effaf3; border-color: #9fd8b5; border-left: 4px solid #1f8f52; }
.card.subset strong { color: #0f6b3a; } .card small { display: block; color: #3d6b50; font-size: 7.5pt; }
.card.cross-os { background: #fff8cc; border-color: #e6ca61; border-left: 4px solid #b88a00; }
.card.cross-os strong { color: #765900; }
.card.cross-os small { color: #765900; }
.cross-os-summary { break-inside: avoid; }
.cross-os-summary table { background: #fff8cc; border: 1px solid #e6ca61; }
.cross-os-summary th { background: #f5e8a5; }
.subset-caption { margin: 2px 0 0; font-weight: 600; color: #0f6b3a; font-size: 9pt; }
.denominator-note { margin: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 4px 0 10px; page-break-inside: auto; }
th, td { text-align: left; border-bottom: 1px solid #e3e6ea; padding: 2px 4px; vertical-align: top; }
th { background: #f5f6f8; } tr { page-break-inside: avoid; } td.num { text-align: right; white-space: nowrap; }
.bar { background: #e6ebf2; height: 8px; width: 120px; position: relative; }
.fill { background: #2f6fdd; height: 8px; position: absolute; left: 0; top: 0; }
.ci { border: 1px solid #10294f; height: 4px; position: absolute; top: 1px; border-width: 0 1px; }
.windows-repositories { page: windows-repositories; }
.repos { table-layout: fixed; }
.repos th, .repos td { font-size: 8pt; overflow-wrap: anywhere; }
.repos .repository-analysis { width: 40%; }
.repos p { margin: 2px 0 5px; }
.repos .sources { font-size: 7pt; }
"""


def text(value):
    if isinstance(value, list):
        value = ", ".join(map(str, value))
    return escape("" if value is None else str(value))


def number(value, suffix=""):
    return "N/A" if value is None else f"{value}{suffix}"


def platform_mix(row):
    return ", ".join(f"{text(item['label'])}: {number(item['percent'], '%')}" for item in row.get("platforms", []))


def distribution_table(rows, confidence, platforms=False):
    if not rows or all(row["denominator"] == 0 for row in rows):
        return '<p class="muted">N/A — no eligible repositories.</p>'
    ci = f"{round(confidence * 100)}% CI" if confidence else None
    head = "<tr><th>Category</th><th>Count / n</th><th>Share</th>" + (f"<th>{ci}</th>" if ci else "") + (
        "<th>Target platform distribution</th></tr>" if platforms else "<th></th></tr>")
    body = []
    for row in rows:
        percent = row["percent"] or 0
        interval = ""
        bar = f'<div class="fill" style="width:{percent * 1.2:.1f}px"></div>'
        if ci:
            low, high = row.get("ci_low"), row.get("ci_high")
            interval = f'<td class="num">{number(low)}–{number(high, "%")}</td>'
            if low is not None:
                bar += f'<div class="ci" style="left:{low * 1.2:.1f}px;width:{(high - low) * 1.2:.1f}px"></div>'
        last = f"<td>{platform_mix(row)}</td>" if platforms else f'<td><div class="bar">{bar}</div></td>'
        body.append(f"<tr><td>{text(row['label'])}</td><td class=\"num\">{row['count']}/{row['denominator']}</td>"
                    f"<td class=\"num\">{number(row['percent'], '%')}</td>{interval}{last}</tr>")
    return f"<table>{head}{''.join(body)}</table>"


def repository_analysis(repository):
    analysis = repository.get("analysis")
    if not analysis or analysis.get("status") != "success":
        message = (f"Analysis unavailable: {analysis.get('error', 'Unknown error')}"
                   if analysis and analysis.get("status") == "failed"
                   else "Analysis not collected. Run the AI analysis step to populate this column.")
        return f'<p class="muted">{text(message)}</p>'
    parts = []
    sources = {source["id"]: source for source in analysis.get("sources", [])}
    for field, label in (("problem", "Problems solved"), ("development", "Development status"),
                         ("motivation", "Why open source"), ("community", "Latest community feedback")):
        summary = analysis.get(field) or "Not collected. Rerun the AI analysis step."
        parts.append(f"<strong>{label}</strong><p>{text(summary)}</p>")
        links = []
        for source_id in analysis.get(f"{field}_sources", []):
            source = sources.get(source_id)
            if source and source.get("url", "").startswith("https://github.com/"):
                links.append(f'<a href="{text(source["url"])}">{text(source_id)}: {text(source["kind"])}</a>')
        if links:
            parts.append(f'<p class="sources">{"; ".join(links)}</p>')
    if analysis.get("window"):
        parts.append(f'<p class="muted">Feedback window (UTC): {text(analysis["window"]["start"])} '
                     f'→ {text(analysis["window"]["end"])}.</p>')
    parts.append(f'<p class="muted">AI-generated at {text(analysis.get("generated_at"))} '
                 f'with {text(analysis.get("model"))}; verify against sources.</p>')
    if analysis.get("limitations"):
        parts.append(f'<p class="muted">{text(analysis["limitations"])}</p>')
    return "".join(parts)


def cross_os_section(report):
    assessment = cross_os_summary(report)
    complete = assessment["complete"]
    total = assessment["selected"]
    rows = assessment["rows"]
    cards = "".join(
        f'<div class="card cross-os"><strong>{row["count"] if complete else "N/A"}</strong>'
        f'{text(label)}<small>'
        f'{"of " + str(total) + " sampled repositories" if complete else "Review not complete"}</small></div>'
        for label, row in zip(("Cross-OS", "Windows", "Others"),
                              rows if complete else ({}, {}, {})))
    parts = ['<section class="cross-os-summary">', f'<div class="cards">{cards}</div>',
             "<h2>Repository OS groups and primary languages</h2>"]
    if not complete:
        message = ("Cross-OS review not collected. Run python -m discovery.cross_os."
                   if not assessment["assessed"] and not assessment["failed"] else
                   f'Cross-OS review incomplete: {assessment["assessed"]}/{total} assessed, '
                   f'{len(assessment["failed"])} failed, {len(assessment["missing"])} not collected. '
                   "The distribution is withheld; retrieval failures are not counted as Others.")
        parts.append(f'<p class="muted">{text(message)}</p>')
    else:
        parts.append("<table><thead><tr><th>Category</th><th>Repositories</th>"
                     "<th>Most used language</th><th>Second most used</th></tr></thead><tbody>")
        for row in rows:
            languages = []
            for rank in row["top_languages"]:
                languages.append("; ".join(
                    f'{text(item["language"])}: {item["count"]} ({number(item["percent"], "%")})'
                    for item in rank) + (" (tied)" if len(rank) > 1 else ""))
            languages += ["N/A"] * (2 - len(languages))
            parts.append(
                f'<tr><td>{text(row["label"])}</td><td class="num">{row["count"]} '
                f'({number(row["percent"], "%")})</td><td>{languages[0]}</td><td>{languages[1]}</td></tr>')
        parts.append("</tbody></table>")
        parts.append(
            f'<p class="muted">Distribution denominator: all {total} sampled repositories. '
            'Groups are mutually exclusive: Cross-OS first, then Windows candidates excluding Cross-OS, '
            'then Others. Windows indicates a detected Windows signal, not Windows-only support. '
            'Languages use GitHub\'s primary language per repository; percentages are within each category. '
            'Ties are retained. The second column of languages shows the next distinct frequency rank.</p>')
    parts.append(f'<p class="muted">{text(assessment["method"])}</p></section>')
    return "".join(parts)


def build_html(report, pages_url=None):
    metrics, coverage, window = report["metrics"], report["coverage"], report["window"]
    confidence = metrics.get("confidence_level")
    representative = coverage.get("representative_sample") and confidence
    if representative:
        notice = (f"Uniform random sample of {metrics['selected']} repositories drawn from "
                  f"{coverage.get('population_size', 'N/A'):,} public repositories with qualifying human activity in "
                  f"GH Archive. Source-scan shares carry {round(confidence * 100)}% Wilson confidence intervals; worst-case margin "
                  f"for complete scans is ±{number(metrics.get('margin_of_error'))} percentage points.")
    else:
        notice = ("Bounded, non-representative cohort from GitHub GraphQL search (GH Archive fallback). "
                  "Percentages describe the analyzed cohort only; no confidence intervals are reported.")
        if coverage.get("fallback_reason"):
            notice += f" Fallback reason: {coverage['fallback_reason']}"
    cards = [("Sampled repositories", metrics["selected"]), ("Complete scans", metrics["successful"]),
             ("Partial", metrics["partial"]), ("Failed", metrics["failed"]),
             ("No eligible source", metrics.get("not_applicable", 0))]
    if representative:
        cards.insert(0, ("Population (30 days)", f"{coverage.get('population_size', 0):,}"))
    complete = metrics["successful"]
    subset = "".join(
        f'<div class="card subset"><strong>{text(v)}</strong>{text(k)}<small>of {complete} complete scans</small></div>'
        for k, v in (("Windows candidates", metrics["windows_repositories"]),
                     ("Windows applications", metrics["windows_applications"])))
    denominator_note = (
        f"Percentages are calculated only from the {complete} complete scans, excluding {metrics['partial']} partial "
        f"scans, {metrics['failed']} failed scans, and {metrics.get('not_applicable', 0)} repositories with no eligible "
        "source. Each repository is counted in exactly one category, so shares add up to 100%.")
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        f"<title>Public App Development Observatory — {text(window['end'][:10])}</title><style>{CSS}</style></head><body>",
        "<h1>Public App Development Observatory</h1>",
        f"<p class=\"muted\">Window {text(window['start'])} → {text(window['end'])} (UTC) · generated {text(report['generated_at'])}"
        f" · ruleset {text(report['ruleset_version'])} · Microsoft Application Inspector {text(report['inspector_version'])}</p>",
        f"<p class=\"notice\">{text(notice)}</p>",
        '<div class="cards">' + "".join(f'<div class="card"><strong>{text(v)}</strong>{text(k)}</div>' for k, v in cards) + "</div>",
        f'<p class="subset-caption">Subset of the {complete} complete scans</p><div class="cards">{subset}</div>',
        cross_os_section(report),
    ]
    if representative:
        parts.append(f"<p class=\"muted\">Seed {text(coverage.get('seed'))} · {coverage.get('hours_processed')}/"
                     f"{coverage.get('hours_expected')} archive hours · {coverage.get('qualifying_events', 0):,} qualifying events · "
                     f"{len(coverage.get('excluded_after_sampling', []))} sampled repositories replaced because they were "
                     "deleted/private.</p>")
    if pages_url:
        parts.append(f'<p>Interactive dashboard: <a href="{escape(pages_url, quote=True)}">{text(pages_url)}</a></p>')
    for key, title, note in SECTIONS:
        parts.append(f"<h2>{text(title)}</h2>")
        if key in EXCLUSIVE:
            parts.append(f'<p class="denominator-note"><strong>{text(denominator_note)}</strong></p>')
        parts.append(f"<p class=\"muted\">{text(note)}</p>")
        if key == "project_types" and key not in metrics:
            parts.append('<p class="muted">Not collected by this report; rerun the collector to populate project findings.</p>')
        else:
            parts.append(distribution_table(metrics.get(key), confidence if representative else None,
                                            platforms=key == "language_platforms"))
            if key == "project_types" and "project_types_unclassified" in metrics:
                parts.append(f'<p class="muted">Classification coverage: {metrics["project_types_unclassified"]} '
                             'repositories have insufficient application-type evidence in the scanned source. '
                             'They remain in the denominator but are not assigned an application type.</p>')
    compatibility = metrics.get("windows_container_compatibility")
    if compatibility:
        parts.extend([
            "<h2>Windows-container compatibility and containerization potential</h2>",
            f'<p class="muted">{text(compatibility["method"])} '
            "Source indicators do not prove build or runtime compatibility; absence of a Dockerfile is not "
            "proof of incompatibility.</p>",
        ])
        if compatibility.get("candidate_method"):
            parts.append(f'<p class="muted">{text(compatibility["candidate_method"])}</p>')
        parts.extend([
            "<p>The two assessment scopes overlap; their counts must not be added together.</p>",
            "<table><thead><tr><th>Scope</th><th>Assessment</th><th>Repositories</th></tr></thead><tbody>",
        ])
        summary, repositories = report_rows(report)
        parts.extend(
            f"<tr><td>{text(scope)}</td><td>{text(label)}</td><td>{count}</td></tr>"
            for scope, label, count in summary
        )
        parts.append("</tbody></table>")
        if repositories:
            parts.extend([
                "<table><thead><tr><th>Repository</th><th>Existing container evidence</th>"
                "<th>Containerization potential</th><th>Source evidence</th>"
                "</tr></thead><tbody>",
            ])
            for repository, existing, potential, evidence in repositories:
                name = text(repository.get("name"))
                url = repository.get("url", "")
                repository_link = (f'<a href="{escape(url, quote=True)}">{name}</a>'
                                   if url.startswith("https://github.com/") else name)
                parts.append(f"<tr><td>{repository_link}</td><td>{text(existing)}</td>"
                             f"<td>{text(potential)}</td><td>{text(evidence)}</td></tr>")
            parts.append("</tbody></table>")
    rows = "".join(
        f"<tr><td>{text(r['name'])}</td><td>{text(r['status'])}</td><td>{text(r.get('primary_language'))}</td>"
        f"<td>{text(r.get('primary_platform'))}</td><td>{text(r.get('primary_framework'))}</td>"
        f"<td>{text(r.get('application_types'))}</td><td>{text(r.get('components'))}</td>"
        f'<td class="repository-analysis">{repository_analysis(r)}</td></tr>'
        for r in report["repositories"]
        if is_windows_candidate(r))
    parts.append('<section class="windows-repositories"><h2>Identified Windows repositories</h2>'
                 "<p class=\"muted\">Windows candidates: complete scans with a Windows platform signal, including "
                 "libraries/tools, excluding repositories classified as Cross-OS. Community feedback is limited to the report window "
                 "and the collected sample, not a live or community-wide assessment.</p>"
                 "<table class=\"repos\"><thead><tr><th>Repository</th><th>Scan</th><th>Language</th>"
                 "<th>Platform</th><th>Framework</th><th>Windows app type</th><th>Windows components</th>"
                 f'<th class="repository-analysis">Repository analysis</th></tr></thead><tbody>{rows}</tbody></table>')
    if not rows:
        parts.append('<p class="muted">No Windows candidates identified.</p>')
    parts.append("<p class=\"muted\">Static, source-level evidence only; detection of a pattern is not proof of runtime use, "
                 "and absence of a match is not proof of non-use. Partial and failed scans are nonresponse and are excluded "
                 "from source-scan distributions, which can bias estimates if they differ systematically. "
                 "The separate cross-OS review retains all sampled repositories.</p></section></body></html>")
    return "".join(parts)


def find_browser():
    for candidate in BROWSERS:
        if candidate and (Path(candidate).is_file() or shutil.which(candidate)):
            return shutil.which(candidate) or candidate
    raise FileNotFoundError("Chrome, Chromium, or Edge is required to print the PDF (set PDF_BROWSER)")


def render_pdf(html, output, browser=None):
    browser = browser or find_browser()
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="report-pdf-", ignore_cleanup_errors=True) as temporary:
        page = Path(temporary) / "report.html"
        page.write_text(html, encoding="utf-8")
        pending = Path(temporary) / "report.pdf"
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
                        "--no-pdf-header-footer", f"--user-data-dir={Path(temporary) / 'profile'}",
                        f"--print-to-pdf={pending}", page.as_uri()],
                       check=True, capture_output=True, timeout=180)
        # Windows Edge/Chrome launchers can exit before the child process finishes writing.
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if pending.is_file() and pending.read_bytes().rstrip().endswith(b"%%EOF"):
                break
            time.sleep(1)
        if not pending.is_file() or pending.read_bytes()[:5] != b"%PDF-":
            raise RuntimeError("Browser did not produce a PDF")
        time.sleep(1)
        shutil.move(pending, output)
    return output


def archive_name(generated_at):
    """Return a sortable, filesystem-safe file name for a report generated at an ISO-8601 time."""
    moment = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("generated_at must include a UTC offset")
    return f"report-{moment.astimezone(timezone.utc):%Y-%m-%d}.pdf"


def archive_pdf(pdf, generated_at, directory):
    """Copy the PDF into directory (created if needed) under its dated name (replacing a same-day report) and return the path."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / archive_name(generated_at)
    shutil.copyfile(pdf, target)
    return target


def main():
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "site" / "report.pdf")
    parser.add_argument("--pages-url", default=os.environ.get("PAGES_URL"))
    parser.add_argument("--archive-dir", type=Path,
                        help="Also copy the PDF here as report-<generated UTC date yyyy-mm-dd>.pdf (e.g. report-history)")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    output = render_pdf(build_html(report, args.pages_url), args.output)
    print(output)
    if args.archive_dir:
        print(archive_pdf(output, report["generated_at"], args.archive_dir))


if __name__ == "__main__":
    main()
