"""Render the saved cross-OS research report and optionally email it.

Run: python -m discovery.research_email [--send]
Uses the existing Gmail configuration; collection is not rerun.
"""

import argparse
from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape
import json
import os
from pathlib import Path
import shutil
import urllib.request

from discovery.report_pdf import render_pdf
from discovery.send_email import send

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "registry-research-2026-11-03.md"
EVIDENCE = (
    REPORT.with_suffix(".json"),
    REPORT.with_name(REPORT.stem + "-independent.json"),
)


def build_html(markdown, repository, ref, token):
    """Render GFM with GitHub, resolving local report links to this branch."""
    request = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": markdown, "mode": "gfm", "context": repository}).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "Accept": "text/html", "User-Agent": "windows-app-discovery"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    base = f"https://github.com/{repository}/blob/{ref}/reports/"
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<base href="{escape(base, quote=True)}">'
        "<style>@page {size: A4 landscape; margin: 12mm}"
        "body {font: 10pt/1.4 Arial,sans-serif; color: #17202a}"
        "table {border-collapse: collapse; width: 100%; font-size: 8pt}"
        "th,td {border: 1px solid #ccd; padding: 4px; vertical-align: top; overflow-wrap: anywhere}"
        "pre,code {white-space: pre-wrap; overflow-wrap: anywhere}"
        "h1,h2,h3 {break-after: avoid} tr {break-inside: avoid}"
        "a {color: #1654a0}</style></head><body>"
        f"{body}</body></html>"
    )


def build_message(markdown_path, pdf_path, evidence_paths, sender, recipient, source_url):
    markdown_path, pdf_path = Path(markdown_path), Path(pdf_path)
    evidence_paths = [Path(path) for path in evidence_paths]
    evidence = [json.loads(path.read_text(encoding="utf-8")) for path in evidence_paths]
    if any(item["window"] != evidence[0]["window"] for item in evidence):
        raise ValueError("Research evidence windows do not match")
    pdf = pdf_path.read_bytes()
    if not pdf.startswith(b"%PDF-") or not pdf.rstrip().endswith(b"%%EOF"):
        raise ValueError(f"{pdf_path} is not a complete PDF")
    message = EmailMessage()
    message["Subject"] = f"[Test] Cross-OS public-source research - window ending {evidence[0]['window']['end'][:10]}"
    message["From"], message["To"] = sender, recipient
    message.set_content(
        "Test-branch research report: original cohort audit plus independent discovery by source.\n"
        f"Evidence window (UTC): {evidence[0]['window']['start']} -> {evidence[0]['window']['end']}\n"
        "This sends the saved research snapshot; discovery was not rerun.\n"
        "The report retains its existing format with one high-level independent-source summary table.\n"
        "Packaging updates and source indicators are not verified runtime compatibility.\n"
        f"Source: {source_url}\n"
        "Attached: PDF and Markdown report.\n"
    )
    message.add_attachment(pdf, maintype="application", subtype="pdf", filename=pdf_path.name)
    message.add_attachment(markdown_path.read_text(encoding="utf-8"), subtype="markdown",
                           filename=markdown_path.name)
    return message


def archive_name(generated_at):
    moment = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("generated_at must include a UTC offset")
    return f"research-analysis-{moment.astimezone(timezone.utc):%Y-%m-%d}.pdf"


def archive_pdf(pdf, generated_at, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / archive_name(generated_at)
    shutil.copyfile(pdf, target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "research-mail")
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--send", action="store_true", help="Send to the configured report recipient")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        raise SystemExit("GH_TOKEN is required to render GitHub Markdown")
    sender = os.environ.get("GMAIL_ADDRESS", "").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    recipient = os.environ.get("REPORT_RECIPIENT", "").strip() or sender
    if args.send and (not sender or not password):
        raise SystemExit("GMAIL_ADDRESS and GMAIL_APP_PASSWORD are required; email not sent")
    repository = os.environ.get("GITHUB_REPOSITORY", "msftjonw-labs/windows-app-discovery")
    ref = os.environ.get("GITHUB_SHA", "main")
    html = build_html(REPORT.read_text(encoding="utf-8"), repository, ref, token)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / (REPORT.stem + ".html")).write_text(html, encoding="utf-8")
    pdf = render_pdf(html, args.output_dir / (REPORT.stem + ".pdf"))
    if args.archive_dir:
        archived = archive_pdf(pdf, datetime.now(timezone.utc).isoformat(), args.archive_dir)
        print(archived)
    for path in (REPORT, *EVIDENCE):
        shutil.copyfile(path, args.output_dir / path.name)
    source_url = f"https://github.com/{repository}/blob/{ref}/reports/{REPORT.name}"
    if args.send:
        send(build_message(REPORT, pdf, EVIDENCE, sender, recipient, source_url), sender, password)
        print("Research report email accepted by SMTP server for the configured recipient.")
    else:
        print(f"Research report rendered to {pdf}; no email sent.")


if __name__ == "__main__":
    main()
