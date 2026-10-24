import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from discovery import report_markdown
from discovery.report_pdf import SECTIONS, build_html
from tests.test_weekly import sample_report


class MarkdownReportTests(unittest.TestCase):
    def test_report_includes_metrics_denominators_and_provenance(self):
        result = report_markdown.build_markdown(sample_report())
        for expected in ("Uniform random sample", "1234567", "95% Wilson", "±10.05",
                         "archive hours: 720/720", "95 complete scans only", "10 / 95", "5.8–18.3%",
                         "Windows applications (subset of complete scans)", "classification error"):
            self.assertIn(expected, result)
        for key, title, _ in SECTIONS:
            self.assertIn(f"![{title}]({key}.svg)", result)

    def test_fallback_suppresses_intervals_even_with_stale_confidence(self):
        report = sample_report(False)
        report["metrics"]["confidence_level"] = 0.95
        result = report_markdown.build_markdown(report)
        self.assertIn("non-representative", result)
        self.assertIn("Fallback reason: down", result)
        self.assertNotIn("Wilson", result)
        self.assertNotIn(" CI |", result)

    def test_untrusted_text_cannot_inject_html_markdown_or_table_rows(self):
        report = sample_report()
        report["repositories"][0]["name"] = '<img src=x> | ![x](https://example.test)\n# heading'
        result = report_markdown.build_markdown(report)
        self.assertNotIn("<script>", result)
        self.assertNotIn("<img", result)
        self.assertIn(r"&lt;img src=x&gt; \| \!\[x\]\(https://example.test\) # heading", result)
        self.assertNotIn("\n# heading", result)

    def test_zero_denominator_is_na_not_zero_percent(self):
        report = sample_report()
        report["metrics"]["components"] = [
            {"label": "Win32", "count": 0, "denominator": 0, "percent": None}]
        result = report_markdown.build_markdown(report)
        section = result.split("## Windows component adoption")[1].split("## Exploratory")[0]
        self.assertIn("N/A — no eligible repositories.", section)
        self.assertNotIn("0%", section)
        svg = report_markdown.chart_svg(report["metrics"]["components"], "Components")
        self.assertIn("N/A", svg)
        self.assertNotIn("0%", "".join(ET.fromstring(svg).itertext()))

    def test_svg_is_valid_xml_and_contains_no_active_content(self):
        svg = report_markdown.chart_svg(sample_report()["metrics"]["platforms"], '<script>"title"</script>')
        root = ET.fromstring(svg)
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertTrue(all(element.tag.rsplit("}", 1)[-1] in {"svg", "title", "rect", "g", "text"}
                            for element in root.iter()))

    def test_writes_complete_bundle_and_overwrites_previous_report(self):
        report = sample_report()
        original = copy.deepcopy(report)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reports"
            report_markdown.write_report(report, output)
            self.assertEqual(len(list(output.iterdir())), len(SECTIONS) + 1)
            for key, _, _ in SECTIONS:
                ET.parse(output / f"{key}.svg")
            report["generated_at"] = "2026-10-26T17:00:00Z"
            report_markdown.write_report(report, output)
            self.assertIn(report["generated_at"], (output / "README.md").read_text(encoding="utf-8"))
            self.assertNotIn(original["generated_at"], (output / "README.md").read_text(encoding="utf-8"))
        report["generated_at"] = original["generated_at"]
        self.assertEqual(report, original)

    def test_weekly_publication_stages_every_generated_chart(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "weekly-report.yml").read_text(encoding="utf-8")
        staging = next(line for line in workflow.splitlines() if "git add --" in line)
        for key, _, _ in SECTIONS:
            self.assertIn(f"reports/{key}.svg", staging)

    def test_no_complete_scans_does_not_create_output(self):
        report = sample_report()
        report["metrics"]["successful"] = 0
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reports"
            with self.assertRaises(ValueError):
                report_markdown.write_report(report, output)
            self.assertFalse(output.exists())

    def test_project_distribution_uses_existing_tables_and_measured_shares(self):
        report = sample_report()
        report["metrics"]["project_types"] = [
            {"label": "Windows desktop app", "count": 2, "denominator": 5, "percent": 40.0,
             "ci_low": 11.76, "ci_high": 76.93},
            {"label": "PowerShell", "count": 1, "denominator": 5, "percent": 20.0,
             "ci_low": 3.62, "ci_high": 62.45}]
        report["metrics"]["unknown_project_platforms"] = [
            {"label": "Web", "count": 3, "denominator": 8, "percent": 37.5},
            {"label": "Windows", "count": 2, "denominator": 8, "percent": 25.0},
            {"label": "Linux", "count": 2, "denominator": 8, "percent": 25.0},
            {"label": "Unknown", "count": 1, "denominator": 8, "percent": 12.5},
        ]
        markdown = report_markdown.build_markdown(report)
        section = markdown.split("## Project application and automation types")[1].split("## Windows application types")[0]
        self.assertIn("categories", section.lower())
        self.assertIn("Categories overlap", section)
        self.assertIn("| Windows desktop app | 2 / 5 | 40.0% | 11.76–76.93% |", section)
        self.assertIn("| PowerShell | 1 / 5 | 20.0%", section)
        self.assertIn("| Web | 3 / 8 | 37.5% |", section)
        self.assertIn("| Others | 5 / 8 | 62.5% |", section)
        self.assertNotIn("| Windows | 2 / 8 |", section)
        html = build_html(report)
        self.assertIn('Windows desktop app</td><td class="num">2/5</td><td class="num">40.0%</td>', html)
        self.assertIn("Unknown / no findings by primary platform", html)
        self.assertIn("Others</td><td class=\"num\">5/8</td>", html)
        svg = report_markdown.chart_svg(report["metrics"]["project_types"], "Project types")
        self.assertIn("PowerShell", svg)
        self.assertIn("20.0%", svg)
        report["coverage"]["representative_sample"] = False
        markdown = report_markdown.build_markdown(report)
        self.assertNotIn(" CI |", markdown)
        self.assertNotIn("<th>95% CI</th>", build_html(report))

    def test_project_distribution_distinguishes_missing_metric_from_empty_population(self):
        report = sample_report()
        report["metrics"].pop("project_types", None)
        for render in (report_markdown.build_markdown, build_html):
            self.assertIn("Not collected by this report", render(report))
        report["metrics"]["project_types"] = [
            {"label": "PowerShell", "count": 0, "denominator": 0, "percent": None}]
        for render in (report_markdown.build_markdown, build_html):
            result = render(report)
            self.assertNotIn("Not collected by this report", result)
            self.assertIn("N/A — no eligible repositories.", result)

    def test_unknown_project_platform_breakdown_uses_strict_thirty_percent_cutoff(self):
        rows = [
            {"label": "Web", "count": 3, "denominator": 10, "percent": 30.0},
            {"label": "Windows", "count": 4, "denominator": 10, "percent": 40.0},
            {"label": "Other platform", "count": 3, "denominator": 10, "percent": 30.0},
        ]
        self.assertEqual(
            report_markdown.unknown_project_platform_rows(rows),
            [{"label": "Windows", "count": 4, "denominator": 10, "percent": 40.0},
             {"label": "Others", "count": 6, "denominator": 10, "percent": 60.0}],
        )

    def test_cli_accepts_input_and_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "report.json"
            source.write_text(json.dumps(sample_report()), encoding="utf-8")
            output = Path(temporary) / "reports"
            with mock.patch("sys.argv", ["report_markdown", "--input", str(source), "--output", str(output)]):
                report_markdown.main()
            self.assertTrue((output / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
