import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.error

from discovery import analysis
from discovery.pilot import PilotError, stamp

START = datetime(2026, 10, 1, tzinfo=timezone.utc)
END = START + timedelta(days=30)
HUMAN = {"__typename": "User", "login": "alice"}
BOT = {"__typename": "Bot", "login": "helper[bot]"}


def comment(body="Please fix startup", when=START, author=HUMAN):
    return {"body": body, "createdAt": stamp(when), "author": author,
            "url": "https://github.com/o/r/issues/1#issuecomment-1"}


def issue(when=START, comments=None):
    return {"title": "Startup issue", "body": "The application will not launch",
            "createdAt": stamp(when), "author": HUMAN, "url": "https://github.com/o/r/issues/1",
            "comments": {"totalCount": 12, "pageInfo": {"hasPreviousPage": True},
                         "nodes": comments or []}}


def github_data(issues):
    return {"repository": {"isPrivate": False, "description": "Desktop task automation",
                           "url": "https://github.com/o/r", "isArchived": False,
                           "pushedAt": stamp(START), "latestRelease": None},
            "recent": {"issueCount": 30, "pageInfo": {"hasNextPage": True}, "nodes": issues},
            "opened": {"issueCount": 15}}


def candidate(**extra):
    return {"name": "o/r", "sha": "abc123", "status": "success", "platforms": ["Windows"], **extra}


def response(summary=None, finish="stop"):
    value = summary or {"problem": "Automates desktop tasks.", "community": "Users report startup friction.",
                        "development": "Development stage is undocumented.",
                        "motivation": "Not documented.", "motivation_sources": ["S1"],
                        "problem_sources": ["S1"], "development_sources": ["S1"], "community_sources": ["S2"]}
    handle = mock.MagicMock()
    handle.__enter__.return_value.read.return_value = json.dumps({
        "choices": [{"finish_reason": finish, "message": {"content": json.dumps(value)}}]
    }).encode()
    return handle


class EvidenceTests(unittest.TestCase):
    @mock.patch.object(analysis, "readme", return_value={"text": "Automates tasks", "truncated": False,
                                                       "url": "https://github.com/o/r/blob/abc123/README.md"})
    @mock.patch.object(analysis, "graphql")
    def test_exact_window_humans_and_count_are_kept_separate(self, graphql, readme):
        graphql.return_value = github_data([issue(comments=[
            comment(), comment(when=END), comment(when=START - timedelta(seconds=1)),
            comment(author=BOT)])])
        evidence = analysis.collect_evidence(candidate(), START, END)
        self.assertEqual(evidence["issues_opened"], 15)
        self.assertEqual(evidence["issues_sampled"], 1)
        self.assertEqual(evidence["comments_sampled"], 1)
        self.assertEqual([source["kind"] for source in evidence["sources"]],
                         ["description", "readme", "repository_status", "issue", "comment"])
        status = json.loads(evidence["sources"][2]["text"])
        self.assertFalse(status["archived"])
        self.assertEqual(status["last_push"], stamp(START))
        self.assertIsNone(status["latest_release"])
        self.assertIn("collected_at", status)
        self.assertIn("created:" + stamp(START) + ".." + stamp(END - timedelta(seconds=1)),
                      graphql.call_args.kwargs["opened"])
        self.assertEqual(graphql.call_args.kwargs["opened"].count("created:"), 1)
        self.assertIn("is:issue", graphql.call_args.kwargs["recent"])
        self.assertIn("older comments omitted: yes", evidence["limitations"])
        readme.assert_called_once_with("o/r", "abc123")

    @mock.patch.object(analysis, "readme", return_value=None)
    @mock.patch.object(analysis, "graphql")
    def test_old_issues_are_context_only_and_excerpts_are_bounded(self, graphql, _):
        graphql.return_value = github_data([
            issue(START - timedelta(days=5), [comment("x" * 900)]),
            issue(END, [comment(when=END)]),
            issue(START - timedelta(days=5)),
        ])
        evidence = analysis.collect_evidence(candidate(), START, END)
        self.assertEqual(evidence["issues_sampled"], 1)
        self.assertEqual(evidence["sources"][2]["kind"], "issue_context")
        self.assertEqual(len(evidence["sources"][3]["text"]), analysis.COMMENT_LENGTH)
        self.assertTrue(evidence["sources"][3]["truncated"])

    @mock.patch.object(analysis, "readme", return_value=None)
    @mock.patch.object(analysis, "graphql")
    def test_archived_and_release_metadata_are_grounded_status_evidence(self, graphql, _):
        data = github_data([])
        data["repository"].update(isArchived=True, latestRelease={
            "tagName": "v1.2", "publishedAt": stamp(START)})
        graphql.return_value = data
        evidence = analysis.collect_evidence(candidate(), START, END)
        status = json.loads(evidence["sources"][1]["text"])
        self.assertTrue(status["archived"])
        self.assertEqual(status["latest_release"]["tagName"], "v1.2")
        self.assertIn("does not establish active maintenance", evidence["limitations"])

    @mock.patch.object(analysis, "readme")
    @mock.patch.object(analysis, "graphql")
    def test_private_repository_is_never_sent_for_analysis(self, graphql, readme):
        graphql.return_value = github_data([])
        graphql.return_value["repository"]["isPrivate"] = True
        with self.assertRaisesRegex(PilotError, "public repository"):
            analysis.collect_evidence(candidate(), START, END)
        readme.assert_not_called()

    @mock.patch.object(analysis.subprocess, "run")
    def test_missing_readme_is_distinct_from_api_failure(self, run):
        run.return_value = mock.Mock(returncode=1, stderr="HTTP 404")
        self.assertIsNone(analysis.readme("o/r", "abc"))
        run.return_value = mock.Mock(returncode=1, stderr="HTTP 403")
        with self.assertRaisesRegex(PilotError, "README request failed"):
            analysis.readme("o/r", "abc")


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {"sources": [{"id": "S1", "kind": "readme", "text": "Automates tasks"},
                                     {"id": "S2", "kind": "comment", "text": "Startup broken"}]}

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_structured_summary_uses_configured_model_and_grounded_ids(self, urlopen):
        urlopen.return_value = response()
        result = analysis.summarize(self.evidence, "test-key", "gpt-4o")
        self.assertEqual(result["problem_sources"], ["S1"])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(payload["model"], "gpt-4o")
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        properties = payload["response_format"]["json_schema"]["schema"]["properties"]
        self.assertEqual(properties["problem_sources"]["items"]["enum"], ["S1", "S2"])
        self.assertEqual(properties["development_sources"]["items"]["enum"], ["S1"])
        self.assertEqual(properties["community_sources"]["items"]["enum"], ["S2"])
        self.assertEqual(properties["community_sources"]["minItems"], 1)
        self.assertIn("untrusted", payload["messages"][0]["content"])
        self.assertIn("Issue volume is NOT sentiment", payload["messages"][0]["content"])

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_invented_and_noncommunity_citations_are_rejected(self, urlopen):
        for citations in (["invented"], ["S1"], [], "S2", [2]):
            with self.subTest(citations=citations):
                urlopen.return_value = response({
                    "problem": "Automation", "motivation": "Sharing", "motivation_sources": ["S1"], "community": "Startup friction",
                    "development": "Undocumented stage", "development_sources": ["S1"],
                    "problem_sources": ["S1"], "community_sources": citations})
                with self.assertRaisesRegex(PilotError, "citations"):
                    analysis.summarize(self.evidence, "key", "gpt-4o")

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_empty_feedback_requires_no_fabricated_citation(self, urlopen):
        urlopen.return_value = response({
            "problem": "Automation", "motivation": "Sharing", "motivation_sources": ["S1"], "community": "Insufficient recent feedback",
            "development": "Undocumented stage", "development_sources": ["S1"],
            "problem_sources": ["S1"], "community_sources": []})
        result = analysis.summarize({"sources": self.evidence["sources"][:1]}, "key", "gpt-4o")
        self.assertEqual(result["community_sources"], [])
        properties = json.loads(urlopen.call_args.args[0].data)["response_format"]["json_schema"]["schema"]["properties"]
        self.assertEqual(properties["community_sources"]["maxItems"], 0)

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_old_issue_context_is_not_a_community_citation_choice(self, urlopen):
        urlopen.return_value = response()
        evidence = {"sources": [*self.evidence["sources"],
                                {"id": "S3", "kind": "issue_context", "text": "Old issue"}]}
        analysis.summarize(evidence, "key", "gpt-4o")
        properties = json.loads(urlopen.call_args.args[0].data)["response_format"]["json_schema"]["schema"]["properties"]
        self.assertEqual(properties["problem_sources"]["items"]["enum"], ["S1", "S2", "S3"])
        self.assertEqual(properties["community_sources"]["items"]["enum"], ["S2"])

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_development_rejects_feedback_citations_and_empty_text(self, urlopen):
        for development, ids in (("Maintained", ["S2"]), ("Maintained", []),
                                 ("", ["S1"]), ("Maintained", ["invented"])):
            with self.subTest(development=development, ids=ids):
                urlopen.return_value = response({
                    "problem": "Automation", "motivation": "Sharing", "motivation_sources": ["S1"], "community": "Startup friction",
                    "development": development, "development_sources": ids,
                    "problem_sources": ["S1"], "community_sources": ["S2"]})
                with self.assertRaisesRegex(PilotError, "development"):
                    analysis.summarize(self.evidence, "key", "gpt-4o")

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_repository_status_is_eligible_for_development_not_feedback(self, urlopen):
        urlopen.return_value = response()
        evidence = {"sources": [*self.evidence["sources"],
                                {"id": "S3", "kind": "repository_status", "text": "Archived"}]}
        analysis.summarize(evidence, "key", "gpt-4o")
        properties = json.loads(urlopen.call_args.args[0].data)["response_format"]["json_schema"]["schema"]["properties"]
        self.assertEqual(properties["development_sources"]["items"]["enum"], ["S1", "S3"])
        self.assertEqual(properties["community_sources"]["items"]["enum"], ["S2"])

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_incomplete_or_invalid_output_is_not_published_as_success(self, urlopen):
        for result in (response(finish="length"), response({"problem": "Only one field"}),
                       response(["not", "an", "object"])):
            urlopen.return_value = result
            with self.assertRaises(PilotError):
                analysis.summarize(self.evidence, "key", "gpt-4o")

    @mock.patch.object(analysis.time, "sleep")
    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_transient_failures_retry_but_auth_failure_is_explicit(self, urlopen, sleep):
        urlopen.side_effect = [
            urllib.error.HTTPError("url", 429, "rate limit", {}, None), response()]
        analysis.summarize(self.evidence, "key", "gpt-4o")
        sleep.assert_called_once()
        urlopen.side_effect = urllib.error.HTTPError("url", 401, "unauthorized", {}, None)
        with self.assertRaisesRegex(PilotError, "HTTP 401"):
            analysis.summarize(self.evidence, "key", "gpt-4o")

    @mock.patch.object(analysis.time, "sleep")
    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_quota_exhaustion_is_actionable_and_not_retried(self, urlopen, sleep):
        for code in ("insufficient_quota", "credit_balance_exhausted"):
            with self.subTest(code=code):
                urlopen.reset_mock()
                body = io.BytesIO(json.dumps({"error": {
                    "code": code, "message": "Private provider details"}}).encode())
                urlopen.side_effect = urllib.error.HTTPError("url", 429, "quota", {}, body)
                with self.assertRaisesRegex(analysis.OpenAIQuotaError, code) as error:
                    analysis.summarize(self.evidence, "key", "gpt-4o")
                self.assertIn("Restore OpenAI API credits/quota", str(error.exception))
                self.assertNotIn("Private provider", str(error.exception))
                urlopen.assert_called_once()
                sleep.assert_not_called()

    @mock.patch.object(analysis.urllib.request, "urlopen")
    def test_malformed_provider_errors_keep_http_diagnostic(self, urlopen):
        for body in (b"not json", b"[]", b'{"error": null}', b'{"error": {"code": []}}'):
            with self.subTest(body=body):
                urlopen.side_effect = urllib.error.HTTPError(
                    "url", 401, "unauthorized", {}, io.BytesIO(body))
                with self.assertRaisesRegex(PilotError, r"OpenAI request failed \(HTTP 401\)"):
                    analysis.summarize(self.evidence, "key", "gpt-4o")


class EnrichmentTests(unittest.TestCase):
    @mock.patch.object(analysis, "summarize")
    @mock.patch.object(analysis, "collect_evidence")
    def test_only_candidates_are_enriched_and_source_text_is_not_published(self, collect, summarize):
        report = {"window": {"start": stamp(START), "end": stamp(END)}, "repositories": [
            candidate(), candidate(status="partial"), candidate(platforms=["Linux"])]}
        collect.return_value = {"sources": [{"id": "S1", "text": "excerpt", "url": "url", "kind": "readme"}]}
        summarize.return_value = {"problem": "Automation", "development": "Experimental",
                                  "community": "Insufficient evidence"}
        analysis.enrich(report, "key", "gpt-4o")
        collect.assert_called_once()
        summarize.assert_called_once()
        self.assertEqual(report["repositories"][0]["analysis"]["status"], "success")
        self.assertEqual(report["repositories"][0]["analysis"]["development"], "Experimental")
        self.assertNotIn("text", report["repositories"][0]["analysis"]["sources"][0])
        self.assertNotIn("analysis", report["repositories"][1])

    @mock.patch.object(analysis, "collect_evidence", side_effect=PilotError("GitHub unavailable"))
    def test_failures_replace_stale_success_with_explicit_diagnostics(self, _):
        repo = candidate(analysis={"status": "success", "problem": "stale"})
        report = {"window": {"start": stamp(START), "end": stamp(END)}, "repositories": [repo]}
        with self.assertLogs("analysis", level="ERROR"):
            analysis.enrich(report, "key", "gpt-4o")
        self.assertEqual(repo["analysis"]["status"], "failed")
        self.assertEqual(repo["analysis"]["error"], "GitHub unavailable")
        self.assertNotIn("problem", repo["analysis"])

    @mock.patch.object(analysis, "summarize")
    @mock.patch.object(analysis, "collect_evidence", return_value={"sources": []})
    def test_quota_exhaustion_stops_requests_without_changing_scan_results(self, collect, summarize):
        report = {"window": {"start": stamp(START), "end": stamp(END)},
                  "metrics": {"windows_repositories": 3}, "repositories": [
                      candidate(), candidate(name="o/second"),
                      candidate(name="o/third", analysis={"status": "success", "problem": "stale"}),
                      candidate(status="partial"), candidate(platforms=["Linux"])]}
        summarize.side_effect = [{"problem": "Automation"},
                                 analysis.OpenAIQuotaError("Restore OpenAI API credits/quota")]
        with self.assertLogs("analysis", level="ERROR"):
            analysis.enrich(report, "key", "gpt-4o")
        self.assertEqual(collect.call_count, 2)
        self.assertEqual(summarize.call_count, 2)
        self.assertEqual(report["repositories"][0]["analysis"]["status"], "success")
        for repo in report["repositories"][1:3]:
            self.assertEqual(repo["status"], "success")
            self.assertEqual(repo["analysis"]["status"], "failed")
            self.assertIn("Restore OpenAI API", repo["analysis"]["error"])
            self.assertNotIn("problem", repo["analysis"])
        self.assertNotIn("analysis", report["repositories"][3])
        self.assertNotIn("analysis", report["repositories"][4])
        self.assertEqual(report["metrics"], {"windows_repositories": 3})

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4o"})
    @mock.patch.object(analysis.time, "sleep")
    @mock.patch.object(analysis.urllib.request, "urlopen")
    @mock.patch.object(analysis, "collect_evidence", return_value={"sources": []})
    def test_command_persists_unavailable_analysis_on_exhausted_credits(self, collect, urlopen, sleep):
        body = io.BytesIO(b'{"error": {"code": "credit_balance_exhausted"}}')
        urlopen.side_effect = urllib.error.HTTPError("url", 429, "quota", {}, body)
        report = {"schema_version": 1, "window": {"start": stamp(START), "end": stamp(END)},
                  "metrics": {"windows_repositories": 2},
                  "repositories": [candidate(), candidate(name="o/second")]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["analysis", "--report", str(path)]), self.assertLogs("analysis"):
                analysis.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["metrics"], report["metrics"])
            self.assertTrue(all(repo["analysis"]["status"] == "failed" for repo in saved["repositories"]))
            self.assertIn("credit_balance_exhausted", saved["repositories"][0]["analysis"]["error"])
            self.assertFalse(path.with_suffix(".tmp").exists())
        collect.assert_called_once()
        urlopen.assert_called_once()
        sleep.assert_not_called()

    @mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-4o"})
    @mock.patch.object(analysis, "collect_evidence")
    @mock.patch.object(analysis, "summarize")
    def test_command_persists_analysis_without_changing_metrics(self, summarize, collect):
        collect.return_value = {"sources": []}
        summarize.return_value = {"problem": "Automation", "development": "Experimental",
                                  "community": "Insufficient evidence"}
        report = {"schema_version": 1, "window": {"start": stamp(START), "end": stamp(END)},
                  "metrics": {"windows_repositories": 1}, "repositories": [candidate()]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            with mock.patch("sys.argv", ["analysis", "--report", str(path)]):
                analysis.main()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["metrics"], report["metrics"])
            self.assertEqual(saved["repositories"][0]["analysis"]["status"], "success")
            self.assertEqual(saved["repositories"][0]["analysis"]["development"], "Experimental")
            self.assertFalse(path.with_suffix(".tmp").exists())
