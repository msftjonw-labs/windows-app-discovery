"""Email the weekly PDF report through Gmail SMTP.

Required environment: GMAIL_ADDRESS, GMAIL_APP_PASSWORD (a Google app password; requires 2-Step
Verification). Optional: REPORT_RECIPIENT (defaults to GMAIL_ADDRESS), PAGES_URL.
Run with: python -m discovery.send_email --report site/data/latest.json --pdf site/report.pdf
"""

import argparse
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import ssl

ROOT = Path(__file__).resolve().parents[1]
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 465


def summary_lines(report):
    metrics, coverage = report["metrics"], report["coverage"]
    lines = [f"Window: {report['window']['start']} -> {report['window']['end']} (UTC)"]
    if coverage.get("representative_sample") and metrics.get("confidence_level"):
        lines.append(f"Random sample: {metrics['selected']} of {coverage.get('population_size', 0):,} active public "
                     f"repositories (GH Archive, seed {coverage.get('seed')}); "
                     f"{round(metrics['confidence_level'] * 100)}% confidence, worst-case margin "
                     f"±{metrics.get('margin_of_error')} pts.")
    else:
        lines.append("Bounded GraphQL-search cohort (GH Archive fallback); not a random sample.")
    lines.append(f"Scans: {metrics['successful']} complete, {metrics['partial']} partial, {metrics['failed']} failed, "
                 f"{metrics.get('not_applicable', 0)} no eligible source.")
    lines.append(f"Windows: {metrics['windows_repositories']} candidates, {metrics['windows_applications']} applications.")
    top = [f"{row['label']} {row['percent']}%" for row in metrics.get("platforms", [])[:5]]
    if top:
        lines.append("Top platforms: " + ", ".join(top))
    components = [f"{row['label']} {row['percent']}%" for row in metrics.get("components", []) if row["count"]]
    if components:
        lines.append("Windows app components: " + ", ".join(components))
    return lines


def build_message(report, pdf_path, sender, recipient, pages_url=None):
    message = EmailMessage()
    message["Subject"] = f"Public App Development Observatory — week ending {report['window']['end'][:10]}"
    message["From"] = sender
    message["To"] = recipient
    body = summary_lines(report)
    if pages_url:
        body.append(f"Dashboard: {pages_url}")
    body.append("The full report is attached as a PDF.")
    message.set_content("\n".join(body) + "\n")
    pdf = Path(pdf_path).read_bytes()
    if pdf[:5] != b"%PDF-":
        raise ValueError(f"{pdf_path} is not a PDF")
    message.add_attachment(pdf, maintype="application", subtype="pdf",
                           filename=f"app-observatory-{report['window']['end'][:10]}.pdf")
    return message


def send(message, sender, password):
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=60) as server:
        server.login(sender, password)
        server.send_message(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--pdf", type=Path, default=ROOT / "site" / "report.pdf")
    args = parser.parse_args()
    sender = os.environ.get("GMAIL_ADDRESS", "").strip()
    # Google displays app passwords in groups separated by spaces.
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    recipient = os.environ.get("REPORT_RECIPIENT", "").strip() or sender
    missing = [name for name, value in (("GMAIL_ADDRESS", sender), ("GMAIL_APP_PASSWORD", password)) if not value]
    if missing:
        raise SystemExit(f"Missing required secret(s): {', '.join(missing)}; email not sent")
    report = json.loads(args.report.read_text(encoding="utf-8"))
    send(build_message(report, args.pdf, sender, recipient, os.environ.get("PAGES_URL")), sender, password)
    print(f"Report emailed to {recipient.split('@')[0][:2]}***@{recipient.split('@')[-1]}")


if __name__ == "__main__":
    main()
