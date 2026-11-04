"""Email the weekly PDF report through Gmail SMTP.

Required environment: GMAIL_ADDRESS, GMAIL_APP_PASSWORD (a Google app password; requires 2-Step
Verification). Optional: REPORT_RECIPIENT (defaults to GMAIL_ADDRESS), PAGES_URL.
Run with: python -m discovery.send_email --report site/data/latest.json --pdf site/report.pdf
Add --gitlab-report gitlab-reports/latest.json --gitlab-pdf gitlab-reports/report.pdf
to send both source reports in one email.
"""

import argparse
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import ssl

from discovery.cross_os import summary as cross_os_summary

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
    elif report.get("source_platform") == "GitLab":
        lines.append("Bounded GitLab.com public-project cohort; not a random sample.")
    else:
        lines.append("Bounded GraphQL-search cohort (GH Archive fallback); not a random sample.")
    lines.append(f"Scans: {metrics['successful']} complete, {metrics['partial']} partial, {metrics['failed']} failed, "
                 f"{metrics.get('not_applicable', 0)} no eligible source.")
    lines.append(f"Windows: {metrics['windows_repositories']} candidates, {metrics['windows_applications']} applications.")
    if "cross_os" in metrics:
        groups = cross_os_summary(report)
        if groups["complete"]:
            lines.append("Exclusive repository groups: " + ", ".join(
                f"{row['label']}: {row['count']} ({row['percent']}%)" for row in groups["rows"]) + ".")
            lines.append("Windows excludes Cross-OS and means a detected Windows signal, not proven Windows-only support.")
        else:
            lines.append("Repository OS groups unavailable: cross-OS evidence review incomplete.")
    compatibility = metrics.get("windows_container_compatibility")
    if compatibility:
        counts = compatibility["counts"]
        lines.append(
            "Windows-container evidence: "
            f"{counts.get('windows_base_image', 0)} Windows base image(s), "
            f"{counts.get('linux_base_image', 0)} Linux base image(s), "
            f"{counts.get('ambiguous_or_mixed_images', 0)} mixed/ambiguous, "
            f"{counts.get('no_container_image_evidence', 0)} with no base-image evidence."
        )
        lines.append("This is static source analysis, not a Windows-container build or runtime test.")
        candidates = compatibility.get("containerization_candidates")
        if candidates:
            lines.append(
                "Windows-targeted, not-yet-containerized suitability screen: "
                f"{candidates.get('potentially_suitable', 0)} potentially suitable, "
                f"{candidates.get('conditional', 0)} conditional, "
                f"{candidates.get('poor_fit', 0)} poor fit, "
                f"{candidates.get('insufficient_evidence', 0)} insufficient evidence."
            )
            lines.append("Suitability is a heuristic; candidates require Windows-container build and runtime validation.")
    top = [f"{row['label']} {row['percent']}%" for row in metrics.get("platforms", [])[:5]]
    if top:
        lines.append("Top platforms: " + ", ".join(top))
    components = [f"{row['label']} {row['percent']}%" for row in metrics.get("components", []) if row["count"]]
    if components:
        lines.append("Windows app components: " + ", ".join(components))
    return lines


def build_message(report, pdf_path, sender, recipient, pages_url=None, gitlab_report=None, gitlab_pdf=None):
    if (gitlab_report is None) != (gitlab_pdf is None):
        raise ValueError("GitLab report metadata and PDF must be supplied together")
    if gitlab_report is not None and (
            gitlab_report.get("source_platform") != "GitLab" or report.get("source_platform") == "GitLab"):
        raise ValueError("Combined email requires a GitHub report and a GitLab report")
    message = EmailMessage()
    message["Subject"] = f"Public App Development Observatory — week ending {report['window']['end'][:10]}"
    if report.get("source_platform") == "GitLab":
        message.replace_header("Subject", f"GitLab — {message['Subject']}")
    message["From"] = sender
    message["To"] = recipient
    body = summary_lines(report)
    if gitlab_report is not None:
        body = ["GitHub report", *body, "", "GitLab report", *summary_lines(gitlab_report)]
    if pages_url:
        body.append(f"Dashboard: {pages_url}")
    body.append("The GitHub and GitLab reports are attached as separate PDFs."
                if gitlab_report is not None else "The full report is attached as a PDF.")
    message.set_content("\n".join(body) + "\n")
    pdf = Path(pdf_path).read_bytes()
    if pdf[:5] != b"%PDF-":
        raise ValueError(f"{pdf_path} is not a PDF")
    message.add_attachment(pdf, maintype="application", subtype="pdf",
                           filename=f"{'gitlab-' if report.get('source_platform') == 'GitLab' else ''}"
                                    f"app-observatory-{report['window']['end'][:10]}.pdf")
    if gitlab_report is not None:
        pdf = Path(gitlab_pdf).read_bytes()
        if pdf[:5] != b"%PDF-":
            raise ValueError(f"{gitlab_pdf} is not a PDF")
        message.add_attachment(pdf, maintype="application", subtype="pdf",
                               filename=f"gitlab-app-observatory-{gitlab_report['window']['end'][:10]}.pdf")
    return message


def send(message, sender, password):
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=60) as server:
        server.login(sender, password)
        server.send_message(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "site" / "data" / "latest.json")
    parser.add_argument("--pdf", type=Path, default=ROOT / "site" / "report.pdf")
    parser.add_argument("--gitlab-report", type=Path, help="GitLab JSON metadata for the second PDF")
    parser.add_argument("--gitlab-pdf", type=Path, help="Attach the GitLab PDF alongside the GitHub PDF")
    args = parser.parse_args()
    if (args.gitlab_report is None) != (args.gitlab_pdf is None):
        parser.error("--gitlab-report and --gitlab-pdf must be supplied together")
    sender = os.environ.get("GMAIL_ADDRESS", "").strip()
    # Google displays app passwords in groups separated by spaces.
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    recipient = os.environ.get("REPORT_RECIPIENT", "").strip() or sender
    missing = [name for name, value in (("GMAIL_ADDRESS", sender), ("GMAIL_APP_PASSWORD", password)) if not value]
    if missing:
        raise SystemExit(f"Missing required secret(s): {', '.join(missing)}; email not sent")
    report = json.loads(args.report.read_text(encoding="utf-8"))
    gitlab_report = (json.loads(args.gitlab_report.read_text(encoding="utf-8"))
                     if args.gitlab_report is not None else None)
    send(build_message(report, args.pdf, sender, recipient, os.environ.get("PAGES_URL"),
                       gitlab_report, args.gitlab_pdf), sender, password)
    print(f"Report emailed to {recipient.split('@')[0][:2]}***@{recipient.split('@')[-1]}")


if __name__ == "__main__":
    main()
