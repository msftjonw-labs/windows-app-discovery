import copy
import json
from pathlib import Path, PurePosixPath
import tempfile
import unittest
from unittest import mock

from discovery import cross_os, report_pdf
from discovery.pilot import PilotError
from tests.test_weekly import sample_report


def sources():
    return [{"id": "S1", "path": "README.md", "url": "https://github.com/o/r/blob/abc/README.md",
             "lines": [{"line": 5, "text": "The example CLI supports Windows and Linux."}]}]


def decision(positive=True):
    return {
        "cross_os": positive, "application": "Example CLI" if positive else "",
        "rationale": "Explicit application support." if positive else "Multi-OS application support not demonstrated.",
        "support": [
            {"os": system, "source_id": "S1", "first_line": 5, "last_line": 5,
             "quote": "The example CLI supports Windows and Linux."}
            for system in ("Windows", "Linux")
        ] if positive else [],
    }


def model_decision():
    result = decision()
    for citation in result["support"]:
        citation.pop("quote")
    return result


def record(name="o/r", language="TypeScript", positive=True, scan_status="success"):
    return {"name": name, "sha": "abc", "status": scan_status, "primary_language": language,
            "cross_os": {"status": "success", "sha": "abc", "decision": decision(positive),
                         "sources": sources() if positive else []}}


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
                     "crates/interconnect/src/__fuzz__/installation/corpus/boundary",
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
    def test_private_repository_is_never_fetched_or_sent(self, github, fetch):
        with self.assertRaisesRegex(PilotError, "public repository"):
            cross_os.collect_evidence({"name": "o/r", "sha": "abc"})
        self.assertEqual(github.call_count, 1)
        fetch.assert_not_called()

    @mock.patch.object(cross_os, "fetch_source_batch", return_value=[None])
    @mock.patch.object(cross_os, "github_json")
    def test_missing_blob_is_not_absence_of_os_support(self, github, _):
        github.side_effect = [{"private": False}, {"truncated": False, "tree": [
            {"path": "README.md", "type": "blob", "size": 2, "sha": "blob"}]}]
        with self.assertRaisesRegex(PilotError, "unavailable"):
            cross_os.collect_evidence({"name": "o/r", "sha": "abc"})


class ReviewTests(unittest.TestCase):
    @mock.patch.object(cross_os, "structured_response", side_effect=lambda *args: model_decision())
    def test_review_uses_strict_application_definition_and_citations(self, request):
        result = cross_os.review({"sources": sources()}, "key", "configured-model")
        self.assertTrue(result["cross_os"])
        self.assertEqual(request.call_args.args[2], "configured-model")
        system = request.call_args.args[3]
        for excluded in ("untrusted", "browser access", "development", "library", "archived upstream", "SAME application"):
            self.assertIn(excluded, system)
        schema = request.call_args.args[4]
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("quote", schema["properties"]["support"]["items"]["properties"])
        self.assertEqual(result["support"][0]["quote"], sources()[0]["lines"][0]["text"])

    @mock.patch.object(cross_os, "structured_response", side_effect=lambda *args: model_decision())
    def test_exact_quotes_are_copied_locally_with_markdown_unicode_and_whitespace(self, _):
        documents = sources()
        documents[0]["lines"][0]["text"] = "  | **Windows** | Linux | macOS \u2014 supported |  "
        result = cross_os.review({"sources": documents}, "key", "model")
        self.assertEqual(result["support"][0]["quote"], documents[0]["lines"][0]["text"])
        cross_os.validate_decision(result, documents)

    @mock.patch.object(cross_os, "structured_response")
    def test_model_cannot_cite_missing_source_lines_or_add_a_fabricated_quote(self, request):
        invalid = []
        value = model_decision()
        value["support"][0]["last_line"] = 6
        invalid.append(value)
        value = model_decision()
        value["support"][0]["source_id"] = "invented"
        invalid.append(value)
        value = model_decision()
        value["support"][0]["quote"] = "invented"
        invalid.append(value)
        for value in invalid:
            request.return_value = value
            with self.subTest(value=value), self.assertRaises(PilotError):
                cross_os.review({"sources": sources()}, "key", "model")

    @mock.patch.object(cross_os, "structured_response")
    def test_invalid_line_reference_gets_one_validated_correction(self, request):
        invalid = model_decision()
        invalid["support"][0]["last_line"] = 6
        request.side_effect = [invalid, model_decision()]
        with self.assertLogs("cross_os", level="WARNING"):
            result = cross_os.review({"sources": sources()}, "key", "model")
        self.assertEqual(request.call_count, 2)
        self.assertIn("omitted lines", request.call_args.args[0]["validation_error"])
        cross_os.validate_decision(result, sources())

    def test_rejects_one_os_invented_sources_quotes_and_line_ranges(self):
        invalid = []
        value = decision()
        value["support"] = value["support"][:1]
        invalid.append(value)
        value = decision()
        value["support"][0]["source_id"] = "invented"
        invalid.append(value)
        value = decision()
        value["support"][0]["quote"] = "The model thinks this supports Windows."
        invalid.append(value)
        value = decision()
        value["support"][0]["last_line"] = 6
        invalid.append(value)
        value = decision()
        value["support"][0]["first_line"] = True
        invalid.append(value)
        value = decision()
        value["support"][0]["os"] = "Ubuntu"
        invalid.append(value)
        value = decision()
        value["application"] = ""
        invalid.append(value)
        value = decision()
        value["cross_os"] = "true"
        invalid.append(value)
        value = decision()
        value["cross_os"] = False
        invalid.append(value)
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(PilotError):
                cross_os.validate_decision(value, sources())

    @mock.patch.object(cross_os, "structured_response")
    def test_no_documents_is_support_not_demonstrated_not_a_model_guess(self, request):
        result = cross_os.review({"sources": []}, "key", "model")
        cross_os.validate_decision(result, [])
        self.assertFalse(result["cross_os"])
        request.assert_not_called()

    def test_only_cited_source_lines_are_retained(self):
        documents = sources()
        documents[0]["lines"].append({"line": 6, "text": "Uncited material"})
        documents.append({"id": "S2", "lines": [{"line": 1, "text": "Unused"}]})
        retained = cross_os.cited_sources(decision(), documents)
        self.assertEqual(retained, sources())


class SummaryTests(unittest.TestCase):
    def test_counts_full_cohort_and_keeps_language_ties(self):
        records = [record(f"o/t{i}") for i in range(6)]
        records += [record(f"o/p{i}", "Python") for i in range(3)]
        records += [record(f"o/g{i}", "Go") for i in range(3)]
        records += [record("o/no-source", "Unknown", False, "not_applicable"),
                    record("o/partial", "Python", False, "partial")]
        summary = cross_os.summary({"repositories": records})
        self.assertTrue(summary["complete"])
        self.assertEqual([row["count"] for row in summary["rows"]], [12, 2])
        first = summary["rows"][0]
        self.assertEqual(first["top_languages"][0][0]["language"], "TypeScript")
        self.assertEqual([x["language"] for x in first["top_languages"][1]], ["Go", "Python"])
        self.assertEqual([x["percent"] for x in first["top_languages"][1]], [25.0, 25.0])

    def test_unavailable_missing_and_stale_reviews_withhold_distribution(self):
        for assessment in (None, {"status": "failed", "error": "API unavailable"},
                           {**record()["cross_os"], "sha": "different"}):
            repository = record()
            repository["cross_os"] = assessment
            summary = cross_os.summary({"repositories": [record("o/good"), repository]})
            self.assertFalse(summary["complete"])
            self.assertEqual(summary["rows"], [])
            self.assertEqual(summary["assessed"], 1)

    def test_empty_categories_and_empty_cohorts_are_explicit(self):
        result = cross_os.summary({"repositories": [record()]})
        self.assertEqual(result["rows"][1]["count"], 0)
        self.assertEqual(result["rows"][1]["top_languages"], [])
        self.assertFalse(cross_os.summary({"repositories": []})["complete"])


class EnrichmentTests(unittest.TestCase):
    @mock.patch.object(cross_os, "review", side_effect=cross_os.OpenAIQuotaError("insufficient_quota"))
    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": sources(), "limitations": []})
    def test_quota_exhaustion_stops_requests_and_withholds_distribution(self, collect, review):
        repositories = [record("o/first"), record("o/second")]
        for repository in repositories:
            repository.pop("cross_os")
        report = {"metrics": {}, "repositories": repositories}
        with self.assertLogs("cross_os", level="ERROR"):
            cross_os.enrich(report, "key", "model")
        collect.assert_called_once()
        review.assert_called_once()
        self.assertEqual(repositories[0]["cross_os"]["status"], "failed")
        self.assertFalse(report["metrics"]["cross_os"]["complete"])
        self.assertEqual(report["metrics"]["cross_os"]["rows"], [])
        self.assertEqual(report["metrics"]["cross_os"]["missing"], ["o/second"])

    @mock.patch.object(cross_os, "review", return_value=decision())
    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": sources(), "limitations": []})
    def test_resumes_validated_same_version_commit_and_model_without_cache(self, collect, review):
        report = {"metrics": {}, "repositories": [record()]}
        cross_os.enrich(report, "key", "model")
        original = copy.deepcopy(report["repositories"][0]["cross_os"])
        cross_os.enrich(report, "key", "model")
        self.assertEqual(collect.call_count, 1)
        self.assertEqual(review.call_count, 1)
        self.assertEqual(report["repositories"][0]["cross_os"], original)
        report["repositories"][0]["cross_os"]["version"] = "old-version"
        cross_os.enrich(report, "key", "model")
        self.assertEqual(collect.call_count, 2)

    @mock.patch.object(cross_os, "collect_evidence")
    def test_tampered_prior_review_cannot_be_resumed_as_success(self, collect):
        repository = record()
        repository["cross_os"].update(version=cross_os.VERSION, model="model")
        repository["cross_os"]["decision"]["support"][0]["quote"] = "invented"
        report = {"metrics": {}, "repositories": [repository]}
        with self.assertLogs("cross_os", level="ERROR"):
            cross_os.enrich(report, "key", "model")
        self.assertEqual(repository["cross_os"]["status"], "failed")
        collect.assert_not_called()
        self.assertFalse(report["metrics"]["cross_os"]["complete"])

    @mock.patch.object(cross_os, "review", return_value=decision())
    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": sources(), "limitations": []})
    def test_caches_by_commit_model_and_version(self, collect, review):
        with tempfile.TemporaryDirectory() as cache:
            report = {"metrics": {}, "repositories": [record(scan_status="partial")]}
            cross_os.enrich(report, "key", "model", cache)
            report["repositories"][0].pop("cross_os")
            cross_os.enrich(report, "key", "model", cache)
            self.assertEqual(collect.call_count, 1)
            self.assertEqual(review.call_count, 1)
            self.assertTrue(report["metrics"]["cross_os"]["complete"])
            report["repositories"][0]["sha"] = "new-sha"
            cross_os.enrich(report, "key", "model", cache)
            self.assertEqual(collect.call_count, 2)
            cross_os.enrich(report, "key", "other-model", cache)
            self.assertEqual(collect.call_count, 3)

    @mock.patch.object(cross_os, "collect_evidence", side_effect=PilotError("GitHub unavailable"))
    def test_error_replaces_stale_success_and_is_not_counted_as_non_cross_os(self, _):
        report = {"metrics": {}, "repositories": [record()]}
        with self.assertLogs("cross_os", level="ERROR"):
            cross_os.enrich(report, "key", "model")
        self.assertEqual(report["repositories"][0]["cross_os"]["status"], "failed")
        self.assertEqual(report["metrics"]["cross_os"]["rows"], [])

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "key", "OPENAI_MODEL": "model"})
    @mock.patch.object(cross_os, "review", return_value=decision())
    @mock.patch.object(cross_os, "collect_evidence", return_value={"sources": sources(), "limitations": []})
    def test_command_persists_success_and_exports_evidence(self, collect, review):
        report = sample_report()
        report["schema_version"] = 1
        report["repositories"] = [record(scan_status="partial")]
        original_metrics = copy.deepcopy(report["metrics"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            export = Path(directory) / "reviews.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["cross_os", "--report", str(path), "--cache", directory,
                                         "--assessments-output", str(export)]):
                cross_os.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(saved["metrics"].pop("cross_os")["complete"])
            self.assertEqual(saved["metrics"], original_metrics)
            self.assertEqual(saved["repositories"][0]["status"], "partial")
            self.assertTrue(json.loads(export.read_text(encoding="utf-8"))["summary"]["complete"])
            self.assertFalse(path.with_suffix(".tmp").exists())

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "", "OPENAI_MODEL": "model"})
    def test_missing_configuration_fails_before_network_or_file_access(self):
        with mock.patch("sys.argv", ["cross_os"]), mock.patch.object(cross_os, "enrich") as enrich, \
                mock.patch("sys.stderr"), self.assertRaises(SystemExit) as result:
            cross_os.main()
        self.assertEqual(result.exception.code, 2)
        enrich.assert_not_called()

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "key", "OPENAI_MODEL": "model"})
    @mock.patch.object(cross_os, "collect_evidence", side_effect=PilotError("API failed"))
    def test_command_persists_failures_and_exits_nonzero(self, _):
        report = sample_report()
        report["schema_version"] = 1
        report["repositories"] = [record()]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["cross_os", "--report", str(path), "--cache", directory]), \
                    self.assertLogs("cross_os", level="ERROR"), self.assertRaisesRegex(SystemExit, "incomplete"):
                cross_os.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["repositories"][0]["cross_os"]["error"], "API failed")
            self.assertFalse(saved["metrics"]["cross_os"]["complete"])
            self.assertFalse(path.with_suffix(".tmp").exists())

    def test_export_retains_provenance_without_changing_original_metrics(self):
        report = sample_report()
        report["repositories"] = [record()]
        original = copy.deepcopy(report["metrics"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.json"
            cross_os.write_assessments(report, path)
            result = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(result["repositories"][0]["cross_os"]["sources"], sources())
            self.assertEqual(result["summary"]["rows"][0]["count"], 1)
            self.assertEqual(report["metrics"], original)


class PdfTests(unittest.TestCase):
    def test_two_yellow_cards_and_language_table_follow_windows_cards(self):
        report = sample_report()
        report["repositories"] = [record("o/ts"), record("o/py", "Python"),
                                  record("o/go", "Go"), record("o/non", "Python", False)]
        html = report_pdf.build_html(report)
        self.assertEqual(html.count('<div class="card cross-os">'), 2)
        self.assertIn("background: #fff8cc", html)
        windows = html.index("Windows applications")
        cross = html.index('<section class="cross-os-summary">')
        table = html.index("<th>Most used language</th>")
        language_section = html.index("<h2>Primary programming languages")
        self.assertLess(windows, cross)
        self.assertLess(cross, table)
        self.assertLess(table, language_section)
        self.assertIn("of 4 sampled repositories", html)
        self.assertIn("Go: 1 (33.33%)", html)
        self.assertIn("(tied)", html)
        self.assertIn("Non-cross-OS", html)
        self.assertIn("not proven incompatibility", html)

    def test_old_reports_do_not_fabricate_counts_and_failures_are_explicit(self):
        report = sample_report()
        html = report_pdf.cross_os_section(report)
        self.assertEqual(html.count("<strong>N/A</strong>"), 2)
        self.assertIn("not collected", html)
        report["repositories"][0]["cross_os"] = {"status": "failed"}
        html = report_pdf.cross_os_section(report)
        self.assertIn("1 failed", html)
        self.assertIn("not counted as non-cross-OS", html)
        self.assertNotIn("<table>", html)

    def test_labels_are_escaped_and_single_language_has_no_fake_runner_up(self):
        report = sample_report()
        report["repositories"] = [record(language="<script>")]
        html = report_pdf.cross_os_section(report)
        self.assertIn("&lt;script&gt;: 1 (100.0%)", html)
        self.assertNotIn("<script>", html)
        self.assertIn("<td>N/A</td>", html)


if __name__ == "__main__":
    unittest.main()
