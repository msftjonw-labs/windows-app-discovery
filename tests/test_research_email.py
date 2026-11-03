import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from discovery.research_email import build_html, build_message


class ResearchEmailTests(unittest.TestCase):
    def test_message_includes_report_and_audit_trails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown, pdf = root / "research.md", root / "research.pdf"
            markdown.write_text("# Research\n", encoding="utf-8")
            pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
            evidence = [root / "cohort.json", root / "independent.json"]
            for path in evidence:
                path.write_text(json.dumps({"window": {"start": "2026-10-03", "end": "2026-11-02"}}))
            message = build_message(markdown, pdf, evidence, "sender@example.com",
                                    "recipient@example.com", "https://example.com/report")
            self.assertEqual(message["To"], "recipient@example.com")
            self.assertTrue(message["Subject"].startswith("[Test]"))
            self.assertIn("discovery was not rerun", message.get_body().get_content())
            self.assertEqual([x.get_filename() for x in message.iter_attachments()],
                             ["research.pdf", "research.md", "cohort.json", "independent.json"])
            evidence[1].write_text(json.dumps({"window": {"start": "different", "end": "window"}}))
            with self.assertRaisesRegex(ValueError, "windows do not match"):
                build_message(markdown, pdf, evidence, "s", "r", "url")
            evidence[1].write_text(evidence[0].read_text())
            pdf.write_bytes(b"%PDF-1.4\nunfinished")
            with self.assertRaisesRegex(ValueError, "complete PDF"):
                build_message(markdown, pdf, evidence, "s", "r", "url")

    @patch("discovery.research_email.urllib.request.urlopen")
    def test_render_uses_pinned_report_link_base(self, urlopen):
        response = MagicMock()
        response.read.return_value = b"<h1>Research</h1>"
        urlopen.return_value.__enter__.return_value = response
        html = build_html("# Research", "owner/repo", "commit-sha", "test-token")
        self.assertIn('href="https://github.com/owner/repo/blob/commit-sha/reports/"', html)
        self.assertIn("<h1>Research</h1>", html)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.github.com/markdown")
        self.assertEqual(json.loads(request.data)["text"], "# Research")
        self.assertNotIn("test-token", html)


if __name__ == "__main__":
    unittest.main()
