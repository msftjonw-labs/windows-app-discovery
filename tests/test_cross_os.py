import copy
import json
from pathlib import Path, PurePosixPath
import tempfile
import unittest
from unittest import mock

from discovery import cross_os, report_pdf
from discovery.pilot import PilotError
from tests.test_weekly import sample_report


def source(text="The application supports Windows and Linux.", path="README.md", line=5):
    return {"id": "S1", "path": path, "url": "https://github.com/o/r/blob/abc/README.md",
            "lines": [{"line": line, "text": text}]}


def assessment(positive=True, sha="abc"):
    evidence = source()
    decision = {
        "cross_os": positive,
        "application": "Repository application" if positive else "",
        "rationale": "Explicit multi-OS support." if positive else "Explicit one-OS-only support.",
        "support": [
            {"os": system, "source_id": "S1", "first_line": 5, "last_line": 5,
             "quote": evidence["lines"][0]["text"]}
            for system in ("Windows", "Linux")
        ] if positive else [],
    }
    return {"version": cross_os.VERSION, "sha": sha, "status": "success",
            "decision": decision, "sources": [evidence] if positive else [],
            "evidence": [] if positive else [{"os": "Linux", "source_id": "S1",
                                               "line": 5, "quote": "Linux only supported"}]}


def record(name="o/r", language="TypeScript", result=None):
    return {"name": name, "sha": "abc", "status": "success", "platforms": ["Windows"],
            "primary_language": language, "primary_platform": "Windows",
            "primary_framework": None, "application_types": [], "components": [],
            "cross_os": copy.deepcopy(result) if result is not None else assessment()}


class EvidenceTests(unittest.TestCase):
    def test_selects_support_documents_and_excludes_irrelevant_trees(self):
        for path in ("README.md", "docs/build.md", "docs/installation.md", "docs/RELEASING.md",
                     "deployment/linux/start_api.sh", ".github/workflows/ci.yml",
                     "apps/desktop/package.json", ".goreleaser.yaml", "app/App.csproj"):
            self.assertTrue(cross_os.eligible_document(PurePosixPath(path)), path)
        for path in ("vendor/lib/README.md", ".agents/skills/support/README.md",
                     "docs/install.png", "node_modules/app/package.json",
                     "docs/upstream-workflows/desktop.yml", "src/main.py", "docs/README.md.png",
                     "src/runtime/__fuzz__/window_archive_groups_rebuild/corpus/boundaries",
                     "src/installation/binary-fixture"):
            self.assertFalse(cross_os.eligible_document(PurePosixPath(path)), path)

    @mock.patch.object(cross_os, "fetch_source_batch")
    @mock.patch.object(cross_os, "github_json")
    def test_pins_requests_preserves_line_numbers_and_records_limits(self, github, fetch):
        github.side_effect = [
            {"private": False},
            {"truncated": True, "tree": [
                {"path": "README.md", "type": "blob", "mode": "100644", "size": 20, "sha": "blob"},
                {"path": "docs/install.md", "type": "blob", "mode": "100644",
                 "size": cross_os.MAX_FILE_BYTES + 1, "sha": "oversize"},
                {"path": "docs/README.md", "type": "blob", "mode": "120000", "size": 1, "sha": "link"},
            ]},
        ]
        fetch.return_value = [b"# Example\n\nThe CLI supports Windows and Linux.\n"]
        result = cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        self.assertEqual(github.call_args.args[0], "repos/o/r/git/trees/abc?recursive=1")
        self.assertEqual(fetch.call_args.args[:2], ("o/r", "abc"))
        self.assertEqual(result["sources"][0]["lines"][2]["line"], 3)
        self.assertIn("/blob/abc/README.md", result["sources"][0]["url"])
        self.assertIn("GitHub source tree truncated", result["limitations"])
        self.assertTrue(any("Oversize" in note for note in result["limitations"]))

    @mock.patch.object(cross_os, "fetch_source_batch")
    @mock.patch.object(cross_os, "github_json", return_value={"private": True})
    def test_private_repository_is_never_fetched(self, github, fetch):
        with self.assertRaisesRegex(PilotError, "public repository"):
            cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        github.assert_called_once()
        fetch.assert_not_called()

    @mock.patch.object(cross_os, "fetch_source_batch", return_value=[b"Supports Windows and Linux."])
    @mock.patch.object(cross_os, "github_json")
    def test_irrelevant_non_windows_paths_do_not_abort_evidence_collection(self, github, fetch):
        github.side_effect = [{"private": False}, {"truncated": False, "tree": [
            {"path": "tests/regression/fire_output_2020-01-01_00:00:00.nc", "type": "blob"},
            {"path": "README.md", "type": "blob", "size": 26, "sha": "blob"},
        ]}]
        result = cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        self.assertEqual([source["path"] for source in result["sources"]], ["README.md"])
        self.assertEqual(fetch.call_args.args[2], [(PurePosixPath("README.md"), 26, "blob")])

    @mock.patch.object(cross_os, "fetch_source_batch")
    @mock.patch.object(cross_os, "github_json")
    def test_eligible_unsafe_paths_still_fail_before_fetch(self, github, fetch):
        github.side_effect = [{"private": False}, {"truncated": False, "tree": [
            {"path": "../README.md", "type": "blob", "size": 1, "sha": "blob"},
        ]}]
        with self.assertRaisesRegex(PilotError, "Unsafe archive path"):
            cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        fetch.assert_not_called()

    @mock.patch.object(cross_os, "fetch_source_batch", return_value=[None])
    @mock.patch.object(cross_os, "github_json")
    def test_missing_blob_is_not_misclassified_as_ambiguous(self, github, _):
        github.side_effect = [{"private": False}, {"truncated": False, "tree": [
            {"path": "README.md", "type": "blob", "size": 2, "sha": "blob"}]}]
        with self.assertRaisesRegex(PilotError, "unavailable"):
            cross_os.collect_evidence({"name": "o/r", "sha": "abc"})

    @mock.patch.object(cross_os, "fetch_source_batch")
    @mock.patch.object(cross_os, "github_json")
    def test_non_text_files_are_logged_and_omitted_without_losing_valid_evidence(self, github, fetch):
        documents = [
            ("README.md", b"\xef\xbb\xbf# Example\r\nSupports Windows and Linux.\r\n"),
            ("docs/install.md", b"\x00\x01Linux\x00"),
            ("docs/support.txt", b"\x00\x00\x00\x00\x00\x00\x80"),
            ("docs/platforms.md", b"Supports macOS.\n"),
        ]
        github.side_effect = [{"private": False}, {"truncated": False, "tree": [
            {"path": path, "type": "blob", "size": len(raw), "sha": f"blob{index}"}
            for index, (path, raw) in enumerate(documents)
        ]}]
        contents = dict(documents)
        fetch.side_effect = lambda name, sha, entries: [contents[str(path)] for path, _, _ in entries]
        with self.assertLogs("cross_os", level="WARNING") as logs:
            result = cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        self.assertEqual(len(logs.output), 2)
        self.assertEqual(result["limitations"], [
            "Binary evidence file omitted: docs/install.md",
            "Non-UTF-8 evidence file omitted: docs/support.txt",
        ])
        self.assertEqual([source["id"] for source in result["sources"]], ["S1", "S2"])
        self.assertEqual([source["path"] for source in result["sources"]],
                         ["README.md", "docs/platforms.md"])
        self.assertEqual(result["sources"][0]["lines"], [
            {"line": 1, "text": "# Example"},
            {"line": 2, "text": "Supports Windows and Linux."},
        ])
        self.assertEqual(result["sources"][1]["lines"], [
            {"line": 1, "text": "Supports macOS."},
        ])

class ClassificationTests(unittest.TestCase):
    def test_explicit_multios_application_support_is_classified_with_exact_citation(self):
        document = source("The desktop application supports Windows, Linux, and macOS.")
        result = cross_os.classify({"sources": [document]})
        self.assertTrue(result["decision"]["cross_os"])
        self.assertEqual({item["os"] for item in result["decision"]["support"]},
                         {"Windows", "Linux", "macOS"})
        self.assertEqual(result["sources"][0]["lines"], document["lines"])
        cross_os.validate_decision(result["decision"], result["sources"])

    def test_explicit_one_os_limit_is_non_cross_os(self):
        result = cross_os.classify({"sources": [
            source("The desktop application is supported on Linux only.")
        ]})
        self.assertFalse(result["decision"]["cross_os"])
        self.assertEqual(result["evidence"][0]["os"], "Linux")

    def test_ambiguous_or_nonapplication_evidence_is_skipped(self):
        cases = [
            source("This project uses Python on Linux and Windows."),
            source("CI runs on Linux and Windows."),
            source("The application may support Windows and Linux."),
            source("Cross-platform development is supported for Windows and Linux.", ".github/workflows/ci.yml"),
            source("The application does not support Windows and Linux."),
            source("The application is available for Windows and Linux.", "scripts/install.sh"),
        ]
        for evidence in cases:
            with self.subTest(evidence=evidence):
                self.assertIsNone(cross_os.classify({"sources": [evidence]}))


class SummaryTests(unittest.TestCase):
    def test_ambiguous_repositories_are_excluded_from_both_category_denominators(self):
        records = [record(f"o/t{i}") for i in range(6)]
        records += [record(f"o/p{i}", "Python") for i in range(3)]
        records += [record(f"o/g{i}", "Go") for i in range(3)]
        records += [record("o/no-source", "Unknown", assessment(False))]
        for index in range(6):
            records.append(record(f"o/ambiguous{index}", result={
                "status": "ambiguous", "sha": "abc", "reason": "unclear"}))
        result = cross_os.summary({"repositories": records})
        self.assertTrue(result["complete"])
        self.assertEqual(result["selected"], 19)
        self.assertEqual(result["assessed"], 13)
        self.assertEqual(result["skipped"], 6)
        self.assertEqual([row["count"] for row in result["rows"]], [12, 1])
        self.assertEqual([row["denominator"] for row in result["rows"]], [13, 13])
        self.assertEqual(result["rows"][0]["percent"], 92.31)
        self.assertEqual(result["rows"][1]["percent"], 7.69)
        self.assertEqual([x["language"] for x in result["rows"][0]["top_languages"][1]],
                         ["Go", "Python"])

    def test_api_failures_withhold_distribution_but_ambiguous_cases_do_not(self):
        records = [record(), record("o/ambiguous", result={
            "status": "ambiguous", "sha": "abc", "reason": "unclear"})]
        result = cross_os.summary({"repositories": records})
        self.assertTrue(result["complete"])
        failed = record("o/failed", result={"status": "failed", "sha": "abc", "error": "API"})
        result = cross_os.summary({"repositories": [records[0], failed]})
        self.assertFalse(result["complete"])
        self.assertEqual(result["rows"], [])

    def test_empty_classifiable_category_and_empty_sample_are_explicit(self):
        result = cross_os.summary({"repositories": [record()]})
        self.assertEqual(result["rows"][1]["count"], 0)
        self.assertEqual(result["rows"][1]["top_languages"], [])
        self.assertFalse(cross_os.summary({"repositories": []})["complete"])


class EnrichmentTests(unittest.TestCase):
    @mock.patch.object(cross_os, "classify", return_value=None)
    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": [], "limitations": []})
    def test_classifies_ambiguous_repositories_without_any_model_client(self, collect, classify):
        report = {"metrics": {}, "repositories": [
            {"name": "o/r", "sha": "abc", "primary_language": "Python"}]}
        cross_os.enrich(report)
        self.assertEqual(report["repositories"][0]["cross_os"]["status"], "ambiguous")
        self.assertTrue(report["metrics"]["cross_os"]["complete"])
        classify.assert_called_once()
        collect.assert_called_once()

    @mock.patch.object(cross_os, "collect_evidence", side_effect=PilotError("GitHub unavailable"))
    def test_github_errors_are_not_counted_as_ambiguous_or_non_cross_os(self, _):
        report = {"metrics": {}, "repositories": [{"name": "o/r", "sha": "abc"}]}
        with self.assertLogs("cross_os", level="ERROR"):
            cross_os.enrich(report)
        self.assertEqual(report["repositories"][0]["cross_os"]["status"], "failed")
        self.assertEqual(report["metrics"]["cross_os"]["rows"], [])

    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": [], "limitations": []})
    def test_command_persists_ambiguous_outcomes_and_exports_assessments(self, _):
        report = sample_report()
        report["schema_version"] = 1
        report["repositories"] = [{"name": "o/r", "sha": "abc", "primary_language": "Python"}]
        original_metrics = copy.deepcopy(report["metrics"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            export = Path(directory) / "assessments.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["cross_os", "--report", str(path),
                                         "--assessments-output", str(export)]):
                cross_os.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(saved["metrics"].pop("cross_os")["complete"])
            self.assertEqual(saved["metrics"], original_metrics)
            self.assertEqual(saved["repositories"][0]["cross_os"]["status"], "ambiguous")
            self.assertEqual(json.loads(export.read_text())["summary"]["skipped"], 1)

    @mock.patch.object(cross_os, "collect_evidence", side_effect=PilotError("GitHub unavailable"))
    def test_command_saves_diagnostics_and_exits_for_api_failures(self, _):
        report = sample_report()
        report["schema_version"] = 1
        report["repositories"] = [{"name": "o/r", "sha": "abc"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["cross_os", "--report", str(path)]), \
                    self.assertLogs("cross_os", level="ERROR"), \
                    self.assertRaisesRegex(SystemExit, "GitHub evidence collection incomplete"):
                cross_os.main()
            self.assertEqual(json.loads(path.read_text())["repositories"][0]["cross_os"]["status"], "failed")


class PdfTests(unittest.TestCase):
    def test_yellow_distribution_follows_windows_cards_and_uses_classifiable_denominator(self):
        report = sample_report()
        report["repositories"] = [record("o/cross"), record("o/single", "Python", assessment(False)),
                                  record("o/unclear", result={"status": "ambiguous", "sha": "abc"})]
        html = report_pdf.build_html(report)
        self.assertEqual(html.count('<div class="card cross-os">'), 2)
        self.assertIn("background: #fff8cc", html)
        self.assertIn(".cross-os-summary table { background: #fff8cc", html)
        self.assertIn("of 2 classifiable; 1 skipped", html)
        windows = html.index("Windows applications")
        cross = html.index('<section class="cross-os-summary">')
        table = html.index("<th>Most used language</th>")
        self.assertLess(windows, cross)
        self.assertLess(cross, table)
        self.assertIn("Distribution denominator: 2 repositories", html)
        self.assertIn("1 of 3 sampled repositories skipped as ambiguous", html)

    def test_api_failures_do_not_render_misleading_partial_distribution(self):
        report = sample_report()
        report["repositories"] = [record(), record("o/fail", result={
            "status": "failed", "sha": "abc", "error": "GitHub API unavailable"})]
        html = report_pdf.cross_os_section(report)
        self.assertIn("<strong>N/A</strong>", html)
        self.assertIn("review incomplete", html.lower())
        self.assertNotIn("<table>", html)


if __name__ == "__main__":
    unittest.main()
