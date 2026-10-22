import re
import unittest
from unittest import mock

from discovery import app_insights


def application(**overrides):
    return {
        "name": "owner/app", "status": "success", "platforms": ["Windows"],
        "purpose": "Application", "windows_scan": "success", **overrides,
    }


class ApplicationInsightsTests(unittest.TestCase):
    def test_collects_readme_feature_issue_pull_request_and_community_counts(self):
        record = application()
        repository = {
            "description": "A note-taking app.",
            "readme": {"text": (
                "# Notepad\n\nA small desktop app for organizing notes.\n\n"
                "## How it works\n\nIt stores notes in a local database.\n")},
            "issues": {"nodes": [{
                "title": "Add export", "state": "OPEN",
                "body": "Support exporting notes to CSV.",
                "labels": {"nodes": [{"name": "feature"}]},
                "comments": {"totalCount": 2}, "reactions": {"totalCount": 3},
            }]},
            "featureIssues": {"nodes": [{
                "title": "Add export", "url": "https://github.com/owner/app/issues/1",
                "body": "Support exporting notes to CSV.", "state": "OPEN",
                "labels": {"nodes": [{"name": "Feature"}]},
                "comments": {"totalCount": 2}, "reactions": {"totalCount": 3},
            }]},
            "pullRequests": {"nodes": [{
                "title": "Implement export", "body": "Add CSV export for saved notes.",
                "state": "MERGED", "merged": True,
                "comments": {"totalCount": 4}, "reactions": {"totalCount": 1},
            }]},
        }
        calls = []

        def fetch(query, **variables):
            calls.append((query, variables))
            return {"repository": repository}

        app_insights.enrich_windows_applications([record], fetch)

        self.assertEqual(calls[0][1], {"owner": "owner", "name": "app"})
        self.assertIn('labels:["feature"]', calls[0][0])
        self.assertEqual(
            len(re.split(r"(?<=[.!?])\s+", record["analysis"])), 3)
        self.assertIn("organizing notes", record["analysis"])
        self.assertIn("stores notes in a local database", record["analysis"])
        self.assertIn("Support exporting notes to CSV", record["analysis"])
        self.assertIn("Add CSV export for saved notes", record["analysis"])
        self.assertIn("1 issue is open", record["analysis"])
        self.assertIn("1 pull request is merged", record["analysis"])
        self.assertIn("6 comments and 4 reactions", record["analysis"])

    def test_only_fully_scanned_windows_applications_are_enriched(self):
        records = [
            application(),
            application(status="partial"),
            application(purpose="Library"),
            application(windows_scan="partial"),
            application(platforms=["Linux"]),
        ]
        fetch = mock.Mock(return_value={"repository": {}})
        app_insights.enrich_windows_applications(records, fetch)
        fetch.assert_called_once()
        self.assertIn("analysis", records[0])
        self.assertTrue(all("analysis" not in record for record in records[1:]))

    def test_api_failure_produces_three_sentence_fallback(self):
        record = application()
        app_insights.enrich_windows_applications(
            [record], lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("offline")))
        self.assertEqual(len(re.split(r"(?<=[.!?])\s+", record["analysis"])), 3)
        self.assertIn("could not be collected", record["analysis"])


if __name__ == "__main__":
    unittest.main()
