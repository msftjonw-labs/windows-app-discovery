from datetime import datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error
import zipfile

from discovery import cross_os, gitlab, pilot, report_markdown, report_pdf, send_email
from tests.test_pilot import archive
from tests.test_weekly import sample_report

START = datetime(2026, 10, 1, tzinfo=timezone.utc)
END = START + timedelta(days=30)
SHA = "a" * 40


def project(identifier=1):
    return {
        "id": identifier, "path_with_namespace": f"group/subgroup/project{identifier}",
        "visibility": "public", "last_activity_at": "2026-10-30T12:00:00Z",
        "default_branch": "release/main", "archived": False,
    }


def event(identifier=1, **values):
    return {
        "id": identifier, "created_at": "2026-10-15T12:00:00Z",
        "author": {"username": "alice"}, "action_name": "opened", "target_type": "Issue",
        "target_iid": 2, **values,
    }


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.sleeps = []
        def sleep(delay):
            self.sleeps.append(delay)
            self.now += delay
        clock = patch("discovery.gitlab.time.monotonic", side_effect=lambda: self.now)
        sleeper = patch("discovery.gitlab.time.sleep", side_effect=sleep)
        clock.start()
        sleeper.start()
        self.addCleanup(clock.stop)
        self.addCleanup(sleeper.stop)

    @staticmethod
    def response(headers=None):
        response = MagicMock()
        response.read.return_value = b'{"ok": true}'
        response.headers = headers or {}
        return response

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_api_query_token_and_bounded_json(self, urlopen):
        response = MagicMock()
        response.read.return_value = b'{"ok": true}'
        urlopen.return_value.__enter__.return_value = response
        self.assertEqual(gitlab.Client("test-token").get("/projects", visibility="public"), {"ok": True})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Private-token"), "test-token")
        self.assertNotIn("Private-token", request.headers)
        self.assertEqual(request.full_url, "https://gitlab.com/api/v4/projects?visibility=public")
        response.read.assert_called_once_with(12 * 1024 * 1024 + 1)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_anonymous_binary_download_and_limit(self, urlopen):
        response = MagicMock()
        response.read.return_value = b"zip!"
        urlopen.return_value.__enter__.return_value = response
        self.assertEqual(gitlab.Client().get("/archive.zip", binary=True, maximum=4), b"zip!")
        self.assertIsNone(urlopen.call_args.args[0].get_header("Private-token"))
        with self.assertRaises(pilot.DownloadLimitError):
            gitlab.Client().get("/archive.zip", binary=True, maximum=3)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_retries_rate_limits_but_surfaces_final_failure_without_token(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("url", 429, "rate limited", {"Retry-After": "3000"}, None)
        client = gitlab.Client("secret-value")
        with self.assertRaisesRegex(pilot.PilotError, "HTTP 429") as raised:
            client.get("/projects")
        self.assertNotIn("secret-value", str(raised.exception))
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(self.sleeps, [3000])
        with self.assertRaisesRegex(pilot.PilotError, "further requests stopped"):
            client.get("/projects/2")
        self.assertEqual(urlopen.call_count, 2)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_global_and_archive_requests_are_paced(self, urlopen):
        urlopen.return_value.__enter__.return_value = self.response()
        client = gitlab.Client()
        client.get("/projects")
        client.get("/projects/1")
        client.get("/projects/1/repository/archive.zip", binary=True)
        client.get("/projects/2")
        client.get("/projects/2/repository/archive.zip", binary=True)
        self.assertEqual(self.sleeps, [1, 1, 1, 14])
        self.assertEqual(urlopen.call_count, 5)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_authenticated_requests_are_paced(self, urlopen):
        urlopen.return_value.__enter__.return_value = self.response()
        client = gitlab.Client("test-token")
        client.get("/projects")
        client.get("/projects/1")
        self.assertEqual(self.sleeps, [0.5])

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_headerless_429_uses_exponential_backoff_and_recovers(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value = self.response()
        urlopen.side_effect = [
            urllib.error.HTTPError("url", 429, "rate limited", {}, None),
            urllib.error.HTTPError("url", 429, "rate limited", {}, None),
            response,
        ]
        self.assertEqual(gitlab.Client().get("/projects"), {"ok": True})
        self.assertEqual(self.sleeps, [60, 120])

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_persistent_429_has_bounded_retries_and_opens_circuit(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("url", 429, "rate limited", {}, None)
        client = gitlab.Client()
        with self.assertRaisesRegex(pilot.PilotError, "HTTP 429"):
            client.get("/projects")
        self.assertEqual(urlopen.call_count, 6)
        self.assertEqual(self.sleeps, [60, 120, 240, 480, 600])
        self.assertEqual(sum(self.sleeps), 1500)
        with self.assertRaises(pilot.PilotError):
            client.get("/projects/2")
        self.assertEqual(urlopen.call_count, 6)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_wait_beyond_recovery_budget_fails_without_early_retry(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("url", 429, "rate limited", {"Retry-After": "7200"}, None)
        client = gitlab.Client()
        with self.assertRaisesRegex(pilot.PilotError, "recovery exhausted"):
            client.get("/projects")
        self.assertEqual(self.sleeps, [])
        self.assertEqual(urlopen.call_count, 1)

    @patch("discovery.gitlab.time.time", return_value=1000)
    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_429_waits_for_later_reset_before_success(self, urlopen, _):
        response = MagicMock()
        response.__enter__.return_value = self.response()
        urlopen.side_effect = [
            urllib.error.HTTPError("url", 429, "rate limited",
                                   {"Retry-After": "60", "RateLimit-Reset": "1400"}, None),
            response,
        ]
        self.assertEqual(gitlab.Client().get("/projects"), {"ok": True})
        self.assertEqual(self.sleeps, [401])

    @patch("discovery.gitlab.time.time", return_value=1000)
    def test_cooldown_supports_dates_reset_headers_and_invalid_values(self, _):
        self.assertEqual(gitlab.Client.cooldown({"Retry-After": "Thu, 01 Jan 1970 00:25:00 GMT"}), 500)
        self.assertEqual(gitlab.Client.cooldown({"RateLimit-Reset": "1600"}), 601)
        self.assertEqual(gitlab.Client.cooldown({"X-RateLimit-Reset": "1700", "Retry-After": "900"}), 900)
        self.assertEqual(gitlab.Client.cooldown({"Retry-After": "bad", "RateLimit-Reset": "bad"}), 0)
        for value in ("nan", "inf", "-10"):
            self.assertEqual(gitlab.Client.cooldown({"Retry-After": value}), 0)

    @patch("discovery.gitlab.time.time", return_value=1000)
    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_successful_response_exhausting_quota_delays_next_request(self, urlopen, _):
        first, second = MagicMock(), MagicMock()
        first.__enter__.return_value = self.response({"RateLimit-Remaining": "0", "RateLimit-Reset": "1400"})
        second.__enter__.return_value = self.response()
        urlopen.side_effect = [first, second]
        client = gitlab.Client()
        client.get("/projects")
        client.get("/projects/1")
        self.assertEqual(self.sleeps, [401])

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_server_errors_remain_bounded_and_do_not_trip_rate_limit_circuit(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("url", 503, "unavailable", {}, None)
        client = gitlab.Client()
        with self.assertRaisesRegex(pilot.PilotError, "HTTP 503"):
            client.get("/projects")
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(self.sleeps, [5, 10])
        self.assertIsNone(client.rate_limit_error)

    @patch("discovery.gitlab.urllib.request.urlopen")
    def test_rejects_non_api_endpoints_and_permission_failures(self, urlopen):
        for endpoint in ("https://other.example/projects", "//other.example/projects"):
            with self.assertRaises(ValueError):
                gitlab.Client().get(endpoint)
        urlopen.assert_not_called()
        urlopen.side_effect = urllib.error.HTTPError("url", 403, "forbidden", {}, None)
        with self.assertRaisesRegex(pilot.PilotError, "HTTP 403"):
            gitlab.Client().get("/projects")
        self.assertEqual(urlopen.call_count, 1)


class ActivityTests(unittest.TestCase):
    def test_accepts_main_equivalent_gitlab_conversation_events(self):
        for values, expected in [
            ({}, "opened"),
            ({"target_type": "MergeRequest", "action_name": "reopened"}, "reopened"),
            ({"target_type": "MergeRequest", "action_name": "approved"}, "approval"),
            ({"target_type": "Note", "action_name": "commented on",
              "note": {"noteable_type": "MergeRequest", "noteable_iid": 8, "system": False}}, "comment"),
        ]:
            self.assertEqual(gitlab.qualifying_event(event(**values), START, END)["kind"], expected)

    def test_excludes_bots_system_notes_pushes_and_outside_window(self):
        for values in [
            {"author": {"username": "alice", "bot": True}},
            {"author": {"username": "project_123_bot_abc"}},
            {"author": {"username": "ci-bot"}},
            {"author": None},
            {"target_type": "Project", "action_name": "pushed to"},
            {"target_type": "Issue", "action_name": "closed"},
            {"created_at": pilot.stamp(END)},
            {"created_at": pilot.stamp(START - timedelta(seconds=1))},
            {"action_name": "commented on", "note": {"noteable_type": "Issue", "system": True}},
            {"action_name": "commented on", "note": {"noteable_type": "Commit"}},
        ]:
            self.assertIsNone(gitlab.qualifying_event(event(**values), START, END), values)
        self.assertIsNotNone(gitlab.qualifying_event(event(created_at=pilot.stamp(START)), START, END))

    def test_discovers_public_projects_with_dated_non_bot_activity(self):
        client = MagicMock()
        client.get.side_effect = [
            [project(1), project(2), project(3)],
            [event(author={"username": "ci-bot"})],
            [event(), event(), event(2, action_name="approved", target_type="MergeRequest", target_iid=7)],
        ]
        candidates, coverage = gitlab.discover(client, 1, START, END)
        self.assertEqual([r["project_id"] for r in candidates], [2])
        self.assertEqual(candidates[0]["observed_events"], 2)
        self.assertIn("https://gitlab.com/group/subgroup/project2/-/merge_requests/7",
                      [e["url"] for e in candidates[0]["activity_evidence"]])
        self.assertFalse(coverage["representative_sample"])
        self.assertEqual(coverage["projects_examined"], 2)
        self.assertEqual(coverage["events_examined"], 4)

    def test_records_event_page_bounds_and_discovery_errors(self):
        client = MagicMock()
        client.get.side_effect = [[project(1), project(2)],
                                  pilot.PilotError("GitLab API HTTP 403"), [event()] * 100]
        candidates, coverage = gitlab.discover(client, 2, START, END, project_budget=2, event_pages=1)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(len(coverage["discovery_errors"]), 1)
        self.assertEqual(coverage["event_history_bounded"], ["group/subgroup/project2"])

    def test_project_pagination_keeps_page_size_constant_with_nonmultiple_budget(self):
        client = MagicMock()
        def get(endpoint, **kwargs):
            if endpoint == "/projects":
                first = 1 if kwargs["page"] == 1 else 101
                return [project(i) for i in range(first, first + 100)]
            return []
        client.get.side_effect = get
        candidates, coverage = gitlab.discover(client, 1, START, END, project_budget=150)
        self.assertEqual(candidates, [])
        self.assertEqual(coverage["projects_examined"], 150)
        pages = [c.kwargs for c in client.get.call_args_list if c.args == ("/projects",)]
        self.assertEqual([p["per_page"] for p in pages], [100, 100])
        self.assertEqual([p["page"] for p in pages], [1, 2])

    def test_stops_before_projects_older_than_window(self):
        client = MagicMock()
        client.get.return_value = [{**project(), "last_activity_at": "2026-09-01T00:00:00Z"}]
        candidates, _ = gitlab.discover(client, 1, START, END)
        self.assertEqual(candidates, [])
        self.assertEqual(client.get.call_count, 1)


class SourceTests(unittest.TestCase):
    def test_pinned_documentation_requires_support_not_ci_or_portability(self):
        data = archive([
            ("root/README.md", "Example app\nRuns on Windows, Linux and macOS.\n"),
            ("root/.gitlab-ci.yml", "supports: Windows Linux\n"),
            ("root/vendor/README.md", "Supports Windows and Linux"),
        ])
        evidence = gitlab.document_evidence(data, "https://gitlab.com/group/sub/app", SHA)
        self.assertEqual(len(evidence["sources"]), 1)
        self.assertIn(f"/-/blob/{SHA}/README.md", evidence["sources"][0]["url"])
        review = cross_os.classify(evidence)
        self.assertTrue(review["decision"]["cross_os"])
        self.assertEqual({x["os"] for x in review["decision"]["support"]}, {"Windows", "Linux", "macOS"})
        ci_only = archive([("root/.gitlab-ci.yml", "Supports Windows and Linux")])
        self.assertFalse(cross_os.classify(gitlab.document_evidence(ci_only, "url", SHA))["decision"]["cross_os"])

    def test_document_limits_binary_and_encoding_are_explicit(self):
        data = archive([("root/README.md", b"\xff"), ("root/INSTALL.txt", b"binary\x00"),
                        ("root/docs/support.md", "Supports Windows and Linux")])
        evidence = gitlab.document_evidence(data, "url", SHA)
        self.assertEqual(len(evidence["limitations"]), 2)
        with patch.object(cross_os, "MAX_DOCUMENTS", 1):
            evidence = gitlab.document_evidence(data, "url", SHA)
        self.assertIn("Document count or source byte bound reached", evidence["limitations"])
        with patch.object(cross_os, "MAX_FILE_BYTES", 1):
            evidence = gitlab.document_evidence(data, "url", SHA)
        self.assertTrue(any("Oversize" in s for s in evidence["limitations"]))

    def test_document_paths_and_symlinks_are_not_extracted(self):
        with self.assertRaises(pilot.PilotError):
            gitlab.document_evidence(archive([("root/../README.md", "bad")]), "url", SHA)
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as z:
            link = zipfile.ZipInfo("root/README.md")
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(link, "Supports Windows and Linux")
        self.assertEqual(gitlab.document_evidence(data.getvalue(), "url", SHA)["sources"], [])

    @patch("discovery.pilot.inspect_sources")
    def test_gitlab_reuses_complete_windows_scan_and_pins_archive_and_citations(self, inspect):
        inspect.return_value = {
            "components": ["Win32"], "frameworks": [], "evidence": [], "incomplete": {},
        }
        client = MagicMock()
        source = archive([
            ("root/README.md", "Supports Windows and Linux."),
            ("root/app.csproj", "<Project><PropertyGroup><OutputType>Exe</OutputType>"
             "<TargetFramework>net8.0-windows</TargetFramework></PropertyGroup></Project>"),
            ("root/Program.cs", "class Program { static void Main() {} }"),
            ("root/.gitlab-ci.yml", "build:\n  tags: [windows]\n  script: dotnet test\n"),
        ])
        client.get.side_effect = [project(), {"id": SHA}, {"C#": 90.0, "Shell": 10.0}, source]
        row = gitlab.analyze_repository(client, {"project_id": 1, "name": "old/name"}, Path("inspector"))
        self.assertEqual(row["sha"], SHA)
        self.assertEqual(row["primary_language"], "C#")
        self.assertEqual(row["status"], "success")
        self.assertEqual(row["windows_scan"], "success")
        self.assertTrue(row["cross_os"]["decision"]["cross_os"])
        inspect.assert_called_once()
        self.assertTrue(row["ci"]["windows"])
        client.get.assert_any_call("/projects/1/repository/commits/release%2Fmain")
        client.get.assert_any_call("/projects/1/repository/archive.zip", sha=SHA, binary=True,
                                  maximum=pilot.MAX_DOWNLOAD)

    def test_private_or_empty_projects_fail_before_download(self):
        for metadata in [{**project(), "visibility": "private"}, {**project(), "default_branch": None}]:
            client = MagicMock()
            client.get.return_value = metadata
            with self.assertRaises(pilot.PilotError):
                gitlab.analyze_repository(client, {"project_id": 1}, Path("inspector"))
            self.assertEqual(client.get.call_count, 1)

    @patch("discovery.gitlab.discover")
    @patch("discovery.gitlab.analyze_repository")
    def test_scan_failure_is_not_counted_as_others(self, analyze, discover):
        discover.return_value = ([{"name": "group/failed", "project_id": 1}], {"representative_sample": False})
        analyze.side_effect = pilot.PilotError("archive limit")
        report = gitlab.collect(MagicMock(), 1, START, END, Path("inspector"))
        self.assertEqual(report["metrics"]["failed"], 1)
        self.assertFalse(report["metrics"]["cross_os"]["complete"])
        self.assertEqual(report["metrics"]["cross_os"]["rows"], [])
        self.assertIsNone(report["metrics"]["confidence_level"])
        self.assertIn("GitLab", report["metrics"]["cross_os"]["method"])


class OutputTests(unittest.TestCase):
    def gitlab_report(self):
        report = sample_report(False)
        report["source_platform"] = "GitLab"
        report["coverage"] = {
            "mode": "bounded-gitlab", "representative_sample": False,
            "projects_examined": 50, "project_budget": 100, "events_examined": 200,
            "event_history_bounded": ["group/bounded"], "discovery_errors": [],
            "activity": gitlab.ACTIVITY,
        }
        return report

    def test_report_and_email_do_not_claim_github_or_random_sample(self):
        report = self.gitlab_report()
        markdown = report_markdown.build_markdown(report)
        html = report_pdf.build_html(report)
        for output in (markdown, html):
            self.assertIn("GitLab", output)
            self.assertIn("non-representative", output)
            self.assertNotIn("GraphQL", output)
            self.assertNotIn("GitHub's primary language", output)
            self.assertNotIn("95% CI", output)
            self.assertNotIn("Wilson", output)
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "report.pdf"
            pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            message = send_email.build_message(report, pdf, "from@example.com", "to@example.com")
        parsed = BytesParser(policy=policy.default).parsebytes(message.as_bytes())
        self.assertTrue(parsed["Subject"].startswith("GitLab"))
        self.assertNotIn("GraphQL", parsed.get_body().get_content())
        self.assertTrue(next(parsed.iter_attachments()).get_filename().startswith("gitlab-"))

    def test_workflow_does_not_touch_github_outputs_or_registries(self):
        workflow = (pilot.ROOT / ".github/workflows/gitlab-report.yml").read_text()
        for expected in ["python -m discovery.gitlab", "gitlab-reports/latest.json",
                         "gitlab-report-history", "secrets.GITLAB_TOKEN"]:
            self.assertIn(expected, workflow)
        for excluded in ["registry-research", "discovery.research_email", "site/data/latest.json",
                         "gharchive", "discovery.analysis", "  schedule:", "  publish:"]:
            self.assertNotIn(excluded, workflow)
        self.assertIn("  workflow_call:", workflow)
        self.assertIn("--archive-prefix gitlab-report", workflow)


class CliTests(unittest.TestCase):
    def run_collection(self, directory, source):
        inspector = directory / "inspector"
        inspector.touch()
        output = directory / "gitlab-reports" / "latest.json"
        client = MagicMock()
        client.get.side_effect = [
            [project()], [event()], project(), {"id": SHA}, {"Python": 100.0}, source,
        ]
        with patch("discovery.gitlab.Client", return_value=client), patch("sys.argv", [
            "gitlab", "--limit", "1", "--project-budget", "1",
            "--end", "2026-10-31T02:00:00+02:00", "--inspector", str(inspector),
            "--output", str(output),
        ]):
            gitlab.main()
        return output

    def test_successful_collection_persists_pinned_report_and_renders_shared_format(self):
        source = archive([
            ("root/main.py", "print('hello')\n"),
            ("root/README.md", "Example application. Supports Windows and Linux.\n"),
        ])
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = self.run_collection(directory, source)
            report = json.loads(output.read_text(encoding="utf-8"))
            assessments = json.loads(output.with_name("cross-os-assessments.json").read_text(encoding="utf-8"))
            self.assertFalse(output.with_suffix(".tmp").exists())
        self.assertEqual(report["window"], {"start": pilot.stamp(START), "end": pilot.stamp(END)})
        self.assertEqual(report["metrics"]["successful"], 1)
        self.assertIsNone(report["metrics"]["confidence_level"])
        self.assertEqual(report["repositories"][0]["sha"], SHA)
        self.assertTrue(report["metrics"]["cross_os"]["complete"])
        self.assertEqual(report["metrics"]["cross_os"]["rows"][0]["count"], 1)
        self.assertEqual(assessments["repositories"][0]["sha"], SHA)
        for rendered in (report_markdown.build_markdown(report), report_pdf.build_html(report)):
            self.assertIn("Cross-OS", rendered)
            self.assertNotIn("GraphQL", rendered)

    def test_failed_collection_saves_diagnostics_and_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(pilot.PilotError, "publishing withheld"):
                self.run_collection(directory, pilot.DownloadLimitError("Archive exceeds limit"))
            output = directory / "gitlab-reports" / "latest.json"
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(output.with_name("cross-os-assessments.json").is_file())
            self.assertEqual(report["metrics"]["failed"], 1)
            self.assertEqual(report["repositories"][0]["error"], "Archive exceeds limit")
            self.assertFalse(report["metrics"]["cross_os"]["complete"])


if __name__ == "__main__":
    unittest.main()
