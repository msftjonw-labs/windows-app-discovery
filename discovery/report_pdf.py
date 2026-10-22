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
    ("platforms", "Target platform", "One primary platform per repository: an explicit OS target wins, several OS "
     "targets = Multiple OS, otherwise the most specific environment; generic runtimes/scripts come last."),
    ("languages", "Primary programming language", "GitHub's primary language per repository."),
    ("frameworks", "Framework evidence", "Most specific detected framework per repository (e.g. Next.js before React)."),
    ("application_types", "Windows application types", "Complete Windows application scans; types can overlap."),
    ("components", "Windows component adoption", "Complete Windows application scans; components overlap."),
    ("candidate_components", "Exploratory: all Windows candidates", "Includes libraries/tools; not an application metric."),
)
EXCLUSIVE = {"platforms", "languages", "frameworks"}
CSS = """
@page { size: Letter; margin: 14mm 12mm; }
body { font: 10pt/1.4 "Segoe UI", Arial, sans-serif; color: #17202a; }
h1 { font-size: 18pt; margin: 0 0 4px; } h2 { font-size: 13pt; margin: 18px 0 6px; border-bottom: 1px solid #ccd; }
.muted { color: #5b6773; } .notice { background: #f3f6fb; border-left: 4px solid #2f6fdd; padding: 6px 10px; }
.cards { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.card { border: 1px solid #ccd; border-radius: 4px; padding: 4px 8px; min-width: 88px; }
.card strong { display: block; font-size: 14pt; }
.card.subset { background: #effaf3; border-color: #9fd8b5; border-left: 4px solid #1f8f52; }
.card.subset strong { color: #0f6b3a; } .card small { display: block; color: #3d6b50; font-size: 7.5pt; }
.subset-caption { margin: 2px 0 0; font-weight: 600; color: #0f6b3a; font-size: 9pt; }
.denominator-note { margin: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 4px 0 10px; page-break-inside: auto; }
th, td { text-align: left; border-bottom: 1px solid #e3e6ea; padding: 2px 4px; vertical-align: top; }
th { background: #f5f6f8; } tr { page-break-inside: avoid; } td.num { text-align: right; white-space: nowrap; }
.bar { background: #e6ebf2; height: 8px; width: 120px; position: relative; }
.fill { background: #2f6fdd; height: 8px; position: absolute; left: 0; top: 0; }
.ci { border: 1px solid #10294f; height: 4px; position: absolute; top: 1px; border-width: 0 1px; }
.repos td { font-size: 8pt; }
"""


def text(value):
    if isinstance(value, list):
        value = ", ".join(map(str, value))
    return escape("" if value is None else str(value))


def number(value, suffix=""):
    return "N/A" if value is None else f"{value}{suffix}"


def distribution_table(rows, confidence):
    if not rows or all(row["denominator"] == 0 for row in rows):
        return '<p class="muted">N/A — no eligible repositories.</p>'
    ci = f"{round(confidence * 100)}% CI" if confidence else None
    head = "<tr><th>Category</th><th>Count / n</th><th>Share</th>" + (f"<th>{ci}</th>" if ci else "") + "<th></th></tr>"
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
        body.append(f"<tr><td>{text(row['label'])}</td><td class=\"num\">{row['count']}/{row['denominator']}</td>"
                    f"<td class=\"num\">{number(row['percent'], '%')}</td>{interval}"
                    f'<td><div class="bar">{bar}</div></td></tr>')
    return f"<table>{head}{''.join(body)}</table>"


def build_html(report, pages_url=None):
    metrics, coverage, window = report["metrics"], report["coverage"], report["window"]
    confidence = metrics.get("confidence_level")
    representative = coverage.get("representative_sample") and confidence
    if representative:
        notice = (f"Uniform random sample of {metrics['selected']} repositories drawn from "
                  f"{coverage.get('population_size', 'N/A'):,} public repositories with qualifying human activity in "
                  f"GH Archive. Shares carry {round(confidence * 100)}% Wilson confidence intervals; worst-case margin "
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
        parts.append(distribution_table(metrics.get(key), confidence if representative else None))
    rows = "".join(
        f"<tr><td>{text(r['name'])}</td><td>{text(r['status'])}</td><td>{text(r.get('primary_language'))}</td>"
        f"<td>{text(r.get('primary_platform'))}</td><td>{text(r.get('primary_framework'))}</td>"
        f"<td>{text(r.get('application_types'))}</td><td>{text(r.get('components'))}</td></tr>"
        for r in report["repositories"])
    parts.append("<h2>Sampled repositories</h2><table class=\"repos\"><tr><th>Repository</th><th>Scan</th><th>Language</th>"
                 f"<th>Platform</th><th>Framework</th><th>Windows app type</th><th>Windows components</th></tr>{rows}</table>")
    parts.append("<p class=\"muted\">Static, source-level evidence only; detection of a pattern is not proof of runtime use, "
                 "and absence of a match is not proof of non-use. Partial and failed scans are nonresponse and are excluded "
                 "from distributions, which can bias estimates if they differ systematically.</p></body></html>")
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
    return f"report-{moment.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}.pdf"


def archive_pdf(pdf, generated_at, directory):
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
                        help="Also copy the PDF here as report-<generated UTC timestamp>.pdf (e.g. report-history)")
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    output = render_pdf(build_html(report, args.pages_url), args.output)
    print(output)
    if args.archive_dir:
        print(archive_pdf(output, report["generated_at"], args.archive_dir))


if __name__ == "__main__":
    main()
