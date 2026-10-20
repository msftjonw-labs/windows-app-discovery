import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from discovery import report_markdown
from discovery.report_pdf import SECTIONS
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
            self.assertEqual(len(list(output.iterdir())), 7)
            for key, _, _ in SECTIONS:
                ET.parse(output / f"{key}.svg")
            report["generated_at"] = "2026-10-26T17:00:00Z"
            report_markdown.write_report(report, output)
            self.assertIn(report["generated_at"], (output / "README.md").read_text(encoding="utf-8"))
            self.assertNotIn(original["generated_at"], (output / "README.md").read_text(encoding="utf-8"))
        report["generated_at"] = original["generated_at"]
        self.assertEqual(report, original)

    def test_no_complete_scans_does_not_create_output(self):
        report = sample_report()
        report["metrics"]["successful"] = 0
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "reports"
            with self.assertRaises(ValueError):
                report_markdown.write_report(report, output)
            self.assertFalse(output.exists())

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
