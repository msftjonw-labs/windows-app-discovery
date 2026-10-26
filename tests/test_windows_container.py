import unittest

from discovery import report_markdown, report_pdf, send_email, windows_container
from tests.test_weekly import sample_report


class WindowsContainerTests(unittest.TestCase):
    def test_extracts_base_images_from_dockerfiles_and_containerfiles(self):
        files = [
            ("Dockerfile", "FROM --platform=linux/amd64 python:3.12 AS build\nRUN make"),
            ("deploy/Containerfile", "FROM mcr.microsoft.com/windows/servercore:ltsc2022"),
            ("README.md", "FROM ubuntu:22.04"),
        ]
        self.assertEqual(windows_container.base_images(files), [
            {"path": "Dockerfile", "line": 1, "image": "python:3.12"},
            {"path": "deploy/Containerfile", "line": 1, "image": "mcr.microsoft.com/windows/servercore:ltsc2022"},
        ])

    def test_classifies_only_explicit_base_image_evidence(self):
        cases = [
            ("windows_base_image", "mcr.microsoft.com/windows/nanoserver:ltsc2022"),
            ("linux_base_image", "ubuntu:24.04"),
            ("ambiguous_or_mixed_images", "company/runtime:latest"),
        ]
        for expected, image in cases:
            with self.subTest(image=image):
                result = windows_container.classify({
                    "status": "success",
                    "container_base_images": [{"path": "Dockerfile", "line": 1, "image": image}],
                })
                self.assertEqual(result["status"], expected)

    def test_absent_and_incomplete_evidence_do_not_claim_incompatibility(self):
        missing = windows_container.classify({"status": "success", "container_base_images": []})
        self.assertEqual(missing["status"], "no_container_image_evidence")
        self.assertIn("does not establish incompatibility", missing["summary"])
        incomplete = windows_container.classify({"status": "partial", "container_base_images": []})
        self.assertEqual(incomplete["status"], "incomplete_scan")

    def test_analyze_report_adds_per_repository_results_and_counts(self):
        report = {
            "repositories": [
                {"status": "success", "container_base_images": [
                    {"path": "Dockerfile", "line": 1, "image": "mcr.microsoft.com/windows/servercore:ltsc2022"}],
                 "platforms": ["Windows"]},
                {"status": "success", "container_base_images": [], "platforms": ["Linux", "Windows"],
                 "projects": [{"labels": ["Backend / API"], "evidence": [
                     {"label": "Backend / API", "path": "src/api.py", "line": 4}]}]},
                {"status": "failed"},
            ],
        }
        result = windows_container.analyze_report(report)
        self.assertEqual(result["repositories"][0]["windows_container"]["status"], "windows_base_image")
        self.assertEqual(result["repositories"][0]["windows_container_candidate"]["status"], "already_containerized")
        self.assertEqual(result["repositories"][1]["windows_container_candidate"]["status"], "potentially_suitable")
        self.assertEqual(result["metrics"]["windows_container_compatibility"]["assessed"], 2)
        self.assertEqual(result["metrics"]["windows_container_compatibility"]["counts"]["incomplete_scan"], 1)

    def test_suitability_screen_uses_windows_target_and_project_evidence(self):
        def record(platforms, labels=(), components=(), configured=False):
            return {
                "status": "success", "platforms": platforms, "components": list(components),
                "container_base_images": [{"path": "Dockerfile", "line": 1, "image": "ubuntu"}]
                if configured else [],
                "projects": [{"labels": list(labels), "evidence": [
                    {"label": label, "path": "src/project.csproj", "line": 10} for label in labels]}],
            }

        self.assertEqual(windows_container.containerization_candidate(
            record(["Windows"], ["Command-line tool"]))["status"], "potentially_suitable")
        self.assertEqual(windows_container.containerization_candidate(
            record(["Linux", "Windows"], ["Backend / API"], ["COM"]))["status"], "conditional")
        self.assertEqual(windows_container.containerization_candidate(
            record(["Windows"], ["WPF"]))["status"], "poor_fit")
        self.assertEqual(windows_container.containerization_candidate(
            record(["Windows"], ["Library / SDK"]))["status"], "insufficient_evidence")
        self.assertEqual(windows_container.containerization_candidate(
            record(["Windows"], ["Backend / API"], configured=True))["status"], "already_containerized")
        self.assertEqual(windows_container.containerization_candidate(
            record(["Linux"], ["Backend / API"]))["status"], "not_windows_targeted")

    def test_reports_and_email_summarize_the_compatibility_assessment(self):
        report = sample_report()
        report["repositories"] = [{
            "name": "owner/project", "url": "https://github.com/owner/project",
            "status": "success", "platforms": ["Windows"],
            "container_base_images": [
                {"path": "Dockerfile", "line": 1, "image": "mcr.microsoft.com/windows/servercore:ltsc2022"}],
            "projects": [{"labels": ["Backend / API"], "evidence": [
                {"label": "Backend / API", "path": "src/api.py", "line": 4}]}],
        }, {
            "name": "owner/uncontainerized", "url": "https://github.com/owner/uncontainerized",
            "status": "success", "platforms": ["Linux", "Windows"],
            "container_base_images": [],
            "projects": [{"labels": ["Backend / API"], "evidence": [
                {"label": "Backend / API", "path": "src/api.py", "line": 4}]}],
        }]
        windows_container.analyze_report(report)
        markdown = report_markdown.build_markdown(report)
        html = report_pdf.build_html(report)
        email = "\n".join(send_email.summary_lines(report))
        for result in (markdown, html, email):
            self.assertIn("Windows base image", result)
        self.assertIn("not proof of incompatibility", markdown)
        self.assertIn("build or runtime compatibility", html)
        self.assertIn("not a Windows-container build or runtime test", email)
        self.assertIn("Dockerfile:1", markdown)
        self.assertIn("mcr.microsoft.com/windows/servercore:ltsc2022", html)
        title = "Windows-container compatibility and containerization potential"
        self.assertIn(title, markdown)
        self.assertIn(title, html)
        markdown_section = markdown.split(f"## {title}", 1)[1]
        html_section = html.split(f"<h2>{title}</h2>", 1)[1].split(
            '<section class="windows-repositories">', 1)[0]
        self.assertEqual(markdown_section.count("| Repository |"), 1)
        self.assertEqual(html_section.count("<th>Repository</th>"), 1)
        self.assertEqual(html_section.count("<table>"), 2)
        self.assertNotIn("### ", markdown_section)
        self.assertNotIn("<h3>", html_section)
        for section in (markdown_section, html_section):
            self.assertEqual(section.count("https://github.com/owner/project"), 1)
            self.assertEqual(section.count("https://github.com/owner/uncontainerized"), 1)
            self.assertIn("counts must not be added together", section)
            self.assertIn("Containerization potential", section)
        self.assertIn("Potentially suitable; validate with a build/run", markdown)
        self.assertIn("src/api.py:4", markdown)
        self.assertIn("1 potentially suitable", email)

    def test_combined_report_preserves_legacy_base_image_results(self):
        report = sample_report()
        report["repositories"][0]["windows_container"] = {
            "summary": "Windows base image configured",
            "evidence": [{"image": "servercore", "image_os": "windows", "path": "Dockerfile", "line": 1}],
        }
        report["repositories"][0]["url"] = "https://github.com/owner/project"
        report["metrics"]["windows_container_compatibility"] = {
            "counts": {"windows_base_image": 1}, "method": "Static analysis",
        }
        for render in (report_markdown.build_markdown, report_pdf.build_html):
            result = render(report)
            self.assertIn("Windows base image configured", result)
            self.assertIn("Suitability analysis not collected.", result)
            self.assertIn("Dockerfile:1", result)


if __name__ == "__main__":
    unittest.main()
