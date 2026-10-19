import gzip
import json
from datetime import datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from discovery import gharchive, pilot, report_pdf, send_email

START = datetime(2026, 10, 1, 5, tzinfo=timezone.utc)


def event(kind, repo_id, login="alice", action="opened", minute=0, public=True, **payload):
    name = f"o/r{repo_id}"
    body = {"action": action, **payload}
    if kind == "IssuesEvent":
        body.setdefault("issue", {"html_url": f"https://github.com/{name}/issues/1", "number": 1})
    if kind == "PullRequestEvent":
        body.setdefault("number", 7)
    if kind in ("IssueCommentEvent", "PullRequestReviewCommentEvent"):
        body.setdefault("comment", {"html_url": f"https://github.com/{name}/issues/1#c{minute}"})
    if kind == "PullRequestReviewEvent":
        body.setdefault("review", {"html_url": f"https://github.com/{name}/pull/1#r{minute}"})
    return json.dumps({
        "id": str(minute), "type": kind, "actor": {"id": 1, "login": login},
        "repo": {"id": repo_id, "name": name}, "payload": body, "public": public,
        "created_at": gharchive.stamp(START + timedelta(minutes=minute)),
    }, separators=(",", ":")).encode()


class ArchiveEventTests(unittest.TestCase):
    def scan(self, lines, k=10):
        return gharchive.scan_lines(lines, "seed", k, START, START + timedelta(hours=1))

    def test_qualifying_events_exclude_bots_and_non_creation_actions(self):
        result = self.scan([
            event("IssuesEvent", 1), event("IssuesEvent", 2, action="labeled"),
            event("PullRequestEvent", 3, login="dependabot[bot]"), event("PullRequestEvent", 4, login="ci-bot"),
            event("IssueCommentEvent", 5, action="created"), event("PushEvent", 6),
            event("PullRequestReviewEvent", 7, action="created"),
            event("PullRequestReviewCommentEvent", 8, action="created"),
            event("PullRequestEvent", 9, action="merged"), event("IssuesEvent", 10, public=False),
        ])
        self.assertEqual(result["ids"], [1, 5, 7, 8])
        self.assertEqual(result["qualifying"], 4)

    def test_pull_request_evidence_is_built_from_trimmed_payload(self):
        result = self.scan([event("PullRequestEvent", 3)])
        self.assertEqual(result["bottom"][0]["activity_evidence"], "https://github.com/o/r3/pull/7")

    def test_events_outside_the_hour_are_ignored(self):
        self.assertEqual(self.scan([event("IssuesEvent", 1, minute=61)])["ids"], [])

    def test_latest_event_supplies_evidence_and_name(self):
        result = self.scan([event("IssueCommentEvent", 1, action="created", minute=30),
                            event("IssuesEvent", 1, minute=5)])
        entry = result["bottom"][0]
        self.assertEqual(entry["observed_events"], 2)
        self.assertEqual(sorted(entry["kinds"]), ["comment", "issue_opened"])
        self.assertTrue(entry["activity_evidence"].endswith("#c30"))


class SamplingTests(unittest.TestCase):
    def hour(self, repo_ids, k, minute=0):
        return gharchive.scan_lines([event("IssuesEvent", i, minute=minute) for i in repo_ids],
                                    "seed", k, START, START + timedelta(hours=1))

    def test_merged_hourly_bottom_k_equals_global_bottom_k(self):
        hours = [self.hour(range(0, 400), 25), self.hour(range(200, 700), 25), self.hour(range(650, 900), 25)]
        sample, population = gharchive.merge(hours, 25)
        expected = sorted(range(900), key=lambda i: gharchive.sample_key("seed", i))[:25]
        self.assertEqual([item["database_id"] for item in sample], expected)
        self.assertEqual(population, 900)
        self.assertEqual([item["sample_rank"] for item in sample], list(range(1, 26)))

    def test_merge_combines_activity_for_sampled_repository_across_hours(self):
        first, second = self.hour([1], 5, minute=1), self.hour([1], 5, minute=50)
        sample, _ = gharchive.merge([first, second], 5)
        self.assertEqual(sample[0]["observed_events"], 2)
        self.assertEqual(sample[0]["last_activity"], gharchive.stamp(START + timedelta(minutes=50)))

    def test_sampling_is_deterministic_and_seed_dependent(self):
        ids = range(5000)
        first = sorted(ids, key=lambda i: gharchive.sample_key("a", i))[:100]
        self.assertEqual(first, sorted(ids, key=lambda i: gharchive.sample_key("a", i))[:100])
        self.assertNotEqual(first, sorted(ids, key=lambda i: gharchive.sample_key("b", i))[:100])

    def test_sampling_is_approximately_uniform(self):
        hits = [0] * 10
        for seed in range(300):
            for repo in sorted(range(1000), key=lambda i: gharchive.sample_key(seed, i))[:100]:
                hits[repo // 100] += 1
        # Each decile expects 3,000 draws; allow generous random variation.
        self.assertTrue(all(2700 < count < 3300 for count in hits), hits)

    def test_window_requires_whole_hours(self):
        self.assertEqual(len(gharchive.window_hours(START, START + timedelta(days=30))), 720)
        with self.assertRaises(ValueError):
            gharchive.window_hours(START + timedelta(minutes=5), START + timedelta(hours=2))


class ArchiveDiscoveryTests(unittest.TestCase):
    def test_too_many_missing_hours_raise_unavailable(self):
        with mock.patch.object(gharchive, "fetch_hour", return_value=None):
            with self.assertRaises(gharchive.ArchiveUnavailable):
                gharchive.discover(START, START + timedelta(hours=3), "seed", reserve=5, workers=1)

    def test_hour_cache_round_trip(self):
        raw = b"\n".join(event("IssuesEvent", i) for i in range(3))
        with tempfile.TemporaryDirectory() as cache:
            with mock.patch.object(gharchive, "fetch_hour", return_value=raw) as fetch:
                first = gharchive.process_hour(START.isoformat(), "seed", 5, cache)
                second = gharchive.process_hour(START.isoformat(), "seed", 5, cache)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(first["ids"], second["ids"])
            self.assertTrue(any(Path(cache).glob("*.json.gz")))


class StatisticsTests(unittest.TestCase):
    def test_wilson_interval_matches_reference_values(self):
        z = pilot.z_score(0.95)
        self.assertAlmostEqual(z, 1.959964, places=5)
        self.assertEqual(pilot.wilson(50, 100, z), (40.38, 59.62))
        self.assertEqual(pilot.wilson(0, 100, z), (0.0, 3.7))
        low, high = pilot.wilson(100, 100, z)
        self.assertEqual(high, 100.0)
        self.assertEqual(pilot.wilson(1, 0, z), (None, None))

    def test_higher_confidence_widens_interval(self):
        narrow = pilot.wilson(30, 100, pilot.z_score(0.95))
        wide = pilot.wilson(30, 100, pilot.z_score(0.99))
        self.assertLess(wide[0], narrow[0])
        self.assertGreater(wide[1], narrow[1])

    def test_aggregate_reports_margin_only_for_random_samples(self):
        records = [{"status": "success", "platforms": ["Linux"], "os_targets": ["Linux"], "frameworks": ["Unknown"],
                    "primary_language": "Go", "purpose": "Library", "windows_scan": "not_applicable",
                    "components": [], "application_types": []}] * 100
        sampled = pilot.aggregate(records, 0.95)
        self.assertEqual(sampled["margin_of_error"], 9.8)
        self.assertEqual(sampled["platforms"][0]["ci_high"], 100.0)
        cohort = pilot.aggregate(records)
        self.assertIsNone(cohort["margin_of_error"])
        self.assertIsNone(cohort["platforms"][0]["ci_low"])


class SampleReplacementTests(unittest.TestCase):
    def test_unavailable_repositories_are_replaced_in_random_order(self):
        candidates = [{"name": f"o/r{i}"} for i in range(5)]

        def analyze(candidate, *_):
            if candidate["name"] in ("o/r1", "o/r2"):
                raise pilot.RepositoryUnavailable("gone")
            if candidate["name"] == "o/r3":
                raise pilot.PilotError("scan failed")
            return {**candidate, "status": "success"}

        with mock.patch.object(pilot, "analyze_repository", side_effect=analyze):
            records, excluded = pilot.analyze_candidates(candidates, 3, Path("x"), Path("c"), skip_unavailable=True)
        self.assertEqual([r["name"] for r in records], ["o/r0", "o/r3", "o/r4"])
        self.assertEqual(records[1]["status"], "failed")
        self.assertEqual([e["name"] for e in excluded], ["o/r1", "o/r2"])

    def test_non_sampled_mode_keeps_unavailable_as_failures(self):
        with mock.patch.object(pilot, "analyze_repository", side_effect=pilot.RepositoryUnavailable("gone")):
            records, excluded = pilot.analyze_candidates([{"name": "o/r"}], 1, Path("x"), Path("c"), False)
        self.assertEqual(records[0]["status"], "failed")
        self.assertEqual(excluded, [])

    def test_renamed_repository_is_resolved_by_numeric_id(self):
        current = {"databaseId": 42, "isPrivate": False, "nameWithOwner": "new/name"}
        responses = [{"repository": None}, {"repository": current}]
        with mock.patch.object(pilot, "graphql", side_effect=responses) as query, \
                mock.patch.object(pilot, "rest_repository_name", return_value="new/name"):
            self.assertIs(pilot.resolve_repository({"name": "old/name", "database_id": 42}), current)
        self.assertEqual(query.call_args.kwargs["owner"], "new")

    def test_reused_name_with_different_id_is_unavailable(self):
        other = {"databaseId": 7, "isPrivate": False}
        with mock.patch.object(pilot, "graphql", return_value={"repository": other}), \
                mock.patch.object(pilot, "rest_repository_name", side_effect=pilot.RepositoryUnavailable("404")):
            with self.assertRaises(pilot.RepositoryUnavailable):
                pilot.resolve_repository({"name": "o/r", "database_id": 42})

    def test_default_archive_end_is_whole_hour_behind_now(self):
        end = pilot.default_archive_end(datetime(2026, 10, 19, 16, 45, tzinfo=timezone.utc))
        self.assertEqual(end, datetime(2026, 10, 19, 13, tzinfo=timezone.utc))


class ExclusiveDistributionTests(unittest.TestCase):
    def test_primary_platform_precedence(self):
        from discovery.rules import primary_framework, primary_platform
        self.assertEqual(primary_platform(["Windows", "Web", "Shell / automation (OS unspecified)"]), "Windows")
        self.assertEqual(primary_platform(["Windows", "Android", "iOS"]), "Multiple OS (incl. Windows)")
        self.assertEqual(primary_platform(["Linux", "macOS"]), "Multiple OS (no Windows)")
        self.assertEqual(primary_platform(["Node.js tooling/runtime (OS unspecified)", "Web", "Server / backend"]), "Web")
        self.assertEqual(primary_platform(["Shell / automation (OS unspecified)"]), "Shell / automation (OS unspecified)")
        self.assertEqual(primary_platform(["Unknown"]), "Unknown")
        self.assertEqual(primary_framework(["Next.js", "React"]), "Next.js")
        self.assertEqual(primary_framework(["React", "React Native"]), "React Native")
        self.assertEqual(primary_framework(["FastAPI", "React", "Svelte"]), "Svelte")
        self.assertEqual(primary_framework(["Unknown"]), "No framework detected")

    def test_exclusive_distributions_sum_to_exactly_100_and_exclude_incomplete(self):
        def record(platforms, frameworks, language, status="success"):
            return {"status": status, "platforms": platforms, "frameworks": frameworks,
                    "primary_language": language, "purpose": "Library", "windows_scan": "not_applicable",
                    "components": [], "application_types": []}
        records = [record(["Web", "Windows"], ["React", "Next.js"], "TypeScript"),
                   record(["Linux"], ["Unknown"], "C"), record(["Web"], ["Vue"], "Vue"),
                   record(["Windows"], ["WPF"], "C#", status="partial"), {"status": "failed", "name": "o/f"}]
        metrics = pilot.aggregate(records, 0.95)
        for key in ("platforms", "frameworks", "languages"):
            rows = metrics[key]
            self.assertEqual(sum(row["count"] for row in rows), 3, key)
            self.assertAlmostEqual(sum(row["percent"] for row in rows), 100.0, places=6, msg=key)
            self.assertTrue(all(row["denominator"] == 3 for row in rows))
        self.assertEqual(sorted(r["percent"] for r in metrics["platforms"]), [33.33, 33.33, 33.34])
        self.assertEqual({r["label"] for r in metrics["platforms"]}, {"Windows", "Linux", "Web"})
        self.assertNotIn("os_targets", metrics)
        self.assertEqual(records[0]["primary_framework"], "Next.js")

    def test_largest_remainder_rounding(self):
        shares = pilot.exclusive_percentages({"a": 1, "b": 1, "c": 1, "d": 4}, 7)
        self.assertAlmostEqual(sum(shares.values()), 100.0, places=6)
        self.assertEqual(shares["d"], 57.14)


def sample_report(representative=True):
    row = {"label": "<script>x</script>", "count": 10, "denominator": 95, "percent": 10.53,
           "ci_low": 5.8 if representative else None, "ci_high": 18.3 if representative else None}
    return {
        "generated_at": "2026-10-19T17:00:00Z", "ruleset_version": "pilot-3", "inspector_version": "1.10.2",
        "window": {"start": "2026-09-19T13:00:00Z", "end": "2026-10-19T13:00:00Z"},
        "coverage": {"representative_sample": representative, "population_size": 1234567, "seed": "s",
                     "hours_processed": 720, "hours_expected": 720, "qualifying_events": 9,
                     "excluded_after_sampling": [], **({} if representative else {"fallback_reason": "down"})},
        "metrics": {"selected": 100, "successful": 95, "partial": 4, "failed": 1, "not_applicable": 0,
                    "windows_repositories": 18, "windows_applications": 13,
                    "confidence_level": 0.95 if representative else None,
                    "margin_of_error": 10.05 if representative else None,
                    **{key: [row] for key, *_ in report_pdf.SECTIONS}},
        "repositories": [{"name": "o/<b>r</b>", "status": "success", "platforms": ["Windows"]}],
    }


class PdfReportTests(unittest.TestCase):
    def test_html_escapes_untrusted_labels_and_shows_intervals(self):
        html = report_pdf.build_html(sample_report(), "https://example.github.io/x/")
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("o/&lt;b&gt;r&lt;/b&gt;", html)
        self.assertIn("95% CI", html)
        self.assertIn("5.8–18.3%", html)
        self.assertIn("1,234,567", html)
        self.assertIn("<strong>Percentages are calculated only from the 95 complete scans, excluding 4 partial", html)
        self.assertIn("Subset of the 95 complete scans", html)
        self.assertNotIn("OS targets only", html)

    def test_fallback_report_is_labeled_without_intervals(self):
        html = report_pdf.build_html(sample_report(representative=False))
        self.assertIn("non-representative", html)
        self.assertIn("Fallback reason: down", html)
        self.assertNotIn("% CI", html)


class EmailTests(unittest.TestCase):
    def test_message_attaches_pdf_and_summarizes_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "r.pdf"
            pdf.write_bytes(b"%PDF-1.4\n%%EOF")
            message = send_email.build_message(sample_report(), pdf, "me@gmail.com", "you@gmail.com", "https://p/")
        parsed = BytesParser(policy=policy.default).parsebytes(message.as_bytes())
        attachment = next(parsed.iter_attachments())
        self.assertEqual(attachment.get_content_type(), "application/pdf")
        self.assertEqual(attachment.get_filename(), "app-observatory-2026-10-19.pdf")
        body = parsed.get_body(("plain",)).get_content()
        self.assertIn("1,234,567", body)
        self.assertIn("±10.05", body)
        self.assertIn("https://p/", body)

    def test_rejects_non_pdf_attachment(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder) / "r.pdf"
            bad.write_bytes(b"<html>")
            with self.assertRaises(ValueError):
                send_email.build_message(sample_report(), bad, "a@gmail.com", "a@gmail.com")

    def test_missing_secrets_fail_without_sending(self):
        with mock.patch.dict("os.environ", {"GMAIL_ADDRESS": "", "GMAIL_APP_PASSWORD": ""}), \
                mock.patch("sys.argv", ["send_email"]), mock.patch.object(send_email, "send") as sender:
            with self.assertRaises(SystemExit) as raised:
                send_email.main()
        self.assertIn("GMAIL_ADDRESS", str(raised.exception))
        sender.assert_not_called()

    def test_send_uses_tls_gmail_and_strips_nothing_secret_into_output(self):
        with mock.patch("smtplib.SMTP_SSL") as smtp:
            send_email.send("message", "me@gmail.com", "app-password")
        smtp.assert_called_once()
        self.assertEqual(smtp.call_args.args, ("smtp.gmail.com", 465))
        smtp.return_value.__enter__.return_value.login.assert_called_once_with("me@gmail.com", "app-password")


if __name__ == "__main__":
    unittest.main()
