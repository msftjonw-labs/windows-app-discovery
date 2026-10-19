from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from discovery.pilot import (
    DownloadLimitError, MAX_FILE, PARTIAL_REASONS, PilotError, acquire_sources, aggregate,
    analyze_repository, application_types, classify, discover, extract_sources, graphql, human,
    fetch_source_batch, inspect_sources, parse_time, qualifying_events, safe_path, selected_sources, source_exclusion,
)


def archive(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as output:
        for name, data in entries:
            output.writestr(name, data)
    return buffer.getvalue()


def issue(created="2026-10-01T00:00:00Z", actor=None):
    return {
        "createdAt": created, "url": "https://github.com/o/r/issues/1",
        "author": actor or {"__typename": "User", "login": "alice"},
        "repository": {"id": "R_1", "nameWithOwner": "o/r", "isPrivate": False},
        "comments": {"nodes": [], "pageInfo": {"hasPreviousPage": False}},
    }


class InspectorBatchTests(unittest.TestCase):
    @patch("discovery.pilot.MAX_INSPECTOR_FILES", 1)
    @patch("discovery.pilot.inspect_source_batch")
    def test_batches_preserve_source_paths_bytes_findings_and_omissions(self, inspect):
        observed = {}

        def scan(source, executable, work):
            for path in source.rglob("*"):
                if path.is_file():
                    observed[path.relative_to(source).as_posix()] = path.read_bytes()
            return {"components": ["COM"], "frameworks": ["WPF"],
                    "evidence": [{"path": next(iter(observed))}],
                    "incomplete": {"filesSkipped": 1}}

        inspect.side_effect = scan
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = work / "source"
            (source / "nested").mkdir(parents=True)
            (source / "nested" / "one.cs").write_bytes(b"class One {}")
            (source / "two.cs").write_bytes(b"class Two {}")
            result = inspect_sources(source, Path("inspector.exe"), work)
            self.assertEqual(list(work.iterdir()), [source])
        self.assertEqual(observed, {"nested/one.cs": b"class One {}", "two.cs": b"class Two {}"})
        self.assertEqual(inspect.call_count, 2)
        self.assertEqual(result["components"], ["COM"])
        self.assertEqual(result["frameworks"], ["WPF"])
        self.assertEqual(result["incomplete"], {"filesSkipped": 2})
        self.assertEqual(len(result["evidence"]), 2)

    @patch("discovery.pilot.MAX_INSPECTOR_BYTES", 5)
    @patch("discovery.pilot.inspect_source_batch")
    def test_byte_budget_splits_batches_without_dropping_large_single_files(self, inspect):
        inspect.return_value = {"components": [], "frameworks": [], "evidence": [], "incomplete": {}}
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = work / "source"
            source.mkdir()
            (source / "one.cs").write_bytes(b"123456")
            (source / "two.cs").write_bytes(b"123")
            inspect_sources(source, Path("inspector.exe"), work)
        self.assertEqual(inspect.call_count, 2)


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.end = parse_time("2026-10-18T12:00:00Z")
        self.start = self.end - timedelta(days=30)

    def test_window_is_exactly_thirty_days(self):
        self.assertEqual(self.end - self.start, timedelta(days=30))
        node = issue("2026-09-18T12:00:00Z")
        self.assertEqual(len(qualifying_events(node, self.start, self.end)), 1)
        node["createdAt"] = "2026-10-18T12:00:00Z"
        self.assertEqual(qualifying_events(node, self.start, self.end), [])
        node["createdAt"] = "2026-09-18T11:59:59Z"
        self.assertEqual(qualifying_events(node, self.start, self.end), [])

    def test_old_issue_with_new_human_comment_qualifies(self):
        node = issue("2020-01-01T00:00:00Z", {"__typename": "Bot", "login": "robot"})
        node["comments"]["nodes"].append({
            "createdAt": "2026-10-17T00:00:00Z",
            "url": "https://github.com/o/r/issues/1#issuecomment-1",
            "author": {"__typename": "User", "login": "alice"},
        })
        self.assertEqual(qualifying_events(node, self.start, self.end)[0]["kind"], "comment")

    def test_bot_and_unknown_accounts_do_not_qualify(self):
        for actor in (None, {"__typename": "Bot", "login": "alice"},
                      {"__typename": "User", "login": "build-bot"},
                      {"__typename": "User", "login": "renovate"}):
            self.assertFalse(human(actor))
        self.assertTrue(human({"__typename": "User", "login": "alice"}))

    def test_review_timestamp_not_creation_timestamp(self):
        node = issue("2020-01-01T00:00:00Z")
        node["reviews"] = {"nodes": [
            {"submittedAt": None, "author": None, "url": "https://github.com/o/r/pull/1"},
            {"submittedAt": "2026-10-17T00:00:00Z",
             "author": {"__typename": "User", "login": "alice"},
             "url": "https://github.com/o/r/pull/1#review-1"},
        ]}
        self.assertEqual(qualifying_events(node, self.start, self.end)[0]["kind"], "review")

    @patch("discovery.pilot.graphql")
    def test_discovery_deduplicates_and_records_truncation(self, api):
        node = issue()
        node["comments"]["pageInfo"]["hasPreviousPage"] = True
        page = {"issueCount": 10000, "nodes": [node],
                "pageInfo": {"hasNextPage": False, "endCursor": "cursor"}}
        api.return_value = {"search": page}
        repos, coverage = discover(10, self.start, self.end)
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["observed_events"], 1)
        self.assertEqual(coverage["truncated_connections"], 2)
        self.assertTrue(all(s["bounded"] for s in coverage["searches"]))

    @patch("discovery.pilot.subprocess.run")
    def test_graphql_partial_error_is_not_success(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = json.dumps({"data": {"search": None}, "errors": [{"message": "denied"}]})
        with self.assertRaisesRegex(PilotError, "GraphQL errors"):
            graphql("query { viewer { login } }")

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            parse_time("2026-10-18T12:00:00")


class ExtractionTests(unittest.TestCase):
    def extract(self, data):
        with tempfile.TemporaryDirectory() as directory:
            return extract_sources(data, Path(directory))

    def test_exclusions_and_partial_scan_indicators(self):
        files, skipped = self.extract(archive([
            ("root/src/main.cs", "class Main {}"),
            ("root/vendor/copied.cs", "System.Windows.Forms"),
            ("root/tests/fake.cs", "CoCreateInstance()"),
            ("root/src/Form.Designer.cs", "generated"),
            ("root/src/legacy.cs", b"\xff\xfeinvalid"),
        ]))
        self.assertEqual([path for path, _ in files], ["src/main.cs"])
        self.assertEqual(skipped["excluded_directories"], 2)
        self.assertEqual(skipped["generated"], 1)
        self.assertEqual(skipped["unsupported_encoding"], 1)

    def test_traversal_and_windows_drive_paths_rejected(self):
        for name in ("root/../../escape.cs", "/absolute.cs", "C:/escape.cs"):
            with self.subTest(name=name), self.assertRaises(PilotError):
                self.extract(archive([(name, "data")]))
        # Python's ZIP writer normalizes backslashes on Windows before serialization.
        with self.assertRaises(PilotError):
            safe_path("root\\escape.cs")

    def test_symlink_skipped_without_following_target(self):
        link = zipfile.ZipInfo("root/link.cs")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            files, skipped = extract_sources(archive([
                (link, "../../outside"), ("root/main.cs", "class Main {}"),
            ]), destination)
            self.assertFalse((destination / "link.cs").exists())
            self.assertEqual(list(destination.iterdir()), [destination / "main.cs"])
        self.assertEqual(files, [("main.cs", "class Main {}")])
        self.assertEqual(skipped["symlinks"], 1)
        self.assertNotIn("symlinks", PARTIAL_REASONS)

    def test_unsafe_symlink_path_still_rejected(self):
        link = zipfile.ZipInfo("root/../../outside.cs")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaisesRegex(PilotError, "Unsafe archive path"):
            self.extract(archive([(link, "target")]))

    def test_utf16_and_utf32_decoded_and_normalized(self):
        text = "class Example { string value = \"\u03a9\"; }\r\n"
        for encoding in ("utf-16", "utf-32", "utf-16-le", "utf-16-be"):
            with self.subTest(encoding=encoding), tempfile.TemporaryDirectory() as directory:
                destination = Path(directory)
                files, skipped = extract_sources(archive([
                    ("root/main.cs", text.encode(encoding)),
                ]), destination)
                self.assertEqual(files, [("main.cs", text.replace("\r\n", "\n"))])
                self.assertEqual(skipped, {})
                self.assertEqual((destination / "main.cs").read_bytes(),
                                 text.replace("\r\n", "\n").encode("utf-8"))

    def test_binary_data_still_skipped(self):
        files, skipped = self.extract(archive([("root/data.cs", b"\x00\x01\x02\x03")]))
        self.assertEqual(files, [])
        self.assertEqual(skipped["binary"], 1)

    def test_lock_and_generated_files_excluded_before_size_limit(self):
        with patch("discovery.pilot.MAX_FILE", 4):
            files, skipped = self.extract(archive([
                ("root/package-lock.json", "x" * 20),
                ("root/pnpm-lock.yaml", "x" * 20),
                ("root/generated.js.map", "x" * 20),
                ("root/main.cs", "x"),
            ]))
        self.assertEqual(files, [("main.cs", "x")])
        self.assertEqual(skipped["generated"], 3)
        self.assertNotIn("oversize_files", skipped)

    def test_oversized_file_skipped(self):
        with patch("discovery.pilot.MAX_FILE", 4):
            files, skipped = self.extract(archive([("root/main.cs", "12345")]))
        self.assertEqual(files, [])
        self.assertEqual(skipped["oversize_files"], 1)

    def test_total_size_limit_fails_instead_of_silent_truncation(self):
        with patch("discovery.pilot.MAX_EXTRACTED", 4):
            with self.assertRaises(PilotError):
                self.extract(archive([("root/a.cs", "123"), ("root/b.cs", "456")]))

    def test_source_scope_retains_code_and_manifests_but_excludes_assets(self):
        for name in ("index.html", "style.css", "main.sh", "Run.ps1", "infra/main.tf",
                     "Dockerfile", "Dockerfile.dev", "package.json", "tsconfig.app.json",
                     "requirements-dev.txt", "CMakeLists.txt", "packages/client/src/main.ts"):
            with self.subTest(name=name):
                self.assertIsNone(source_exclusion(Path(name)))
        for name in ("assets/items.json", "notes.txt", "docs/code.js", "client/testFixture/fake.cs",
                     "datasets/main.py", "assets/readme.json"):
            with self.subTest(name=name):
                self.assertIsNotNone(source_exclusion(Path(name)))


class SelectiveRetrievalTests(unittest.TestCase):
    def tree(self, entries, truncated=False):
        return json.dumps({
            "truncated": truncated,
            "tree": [{"path": path, "size": size, "mode": mode, "type": "blob", "sha": "a" * 40}
                     for path, size, mode in entries],
        })

    @patch("discovery.pilot.selected_sources")
    @patch("discovery.pilot.download", side_effect=DownloadLimitError("large ZIP"))
    def test_large_archive_switches_to_selective_retrieval(self, download, selected):
        selected.return_value = ([("main.cs", "code")], {"symlinks": 1})
        with self.assertLogs("pilot", level="WARNING"):
            files, skipped, method = acquire_sources("owner/repo", "abc", Path("unused"))
        self.assertEqual(method, "selected-files")
        self.assertEqual(files, [("main.cs", "code")])
        self.assertEqual(skipped, {"symlinks": 1})
        selected.assert_called_once_with("owner/repo", "abc", Path("unused"))

    @patch("discovery.pilot.selected_sources")
    @patch("discovery.pilot.download", side_effect=PilotError("not a size error"))
    def test_other_download_failures_are_not_hidden_by_fallback(self, download, selected):
        with self.assertRaisesRegex(PilotError, "not a size error"):
            acquire_sources("owner/repo", "abc", Path("unused"))
        selected.assert_not_called()

    @patch("discovery.pilot.fetch_source_batch", return_value=[b"code"])
    @patch("discovery.pilot.subprocess.run")
    def test_shared_filters_and_pinned_encoded_urls(self, run, download):
        run.return_value.returncode = 0
        run.return_value.stdout = self.tree([
            ("src/main file.cs", 4, "100644"),
            ("vendor/copied.cs", 4, "100644"),
            ("package-lock.json", 10000000, "100644"),
            ("src/link.cs", 4, "120000"),
            ("external", 4, "160000"),
        ])
        with tempfile.TemporaryDirectory() as directory:
            files, skipped = selected_sources("o/r", "deadbeef", Path(directory))
        self.assertEqual(files, [("src/main file.cs", "code")])
        self.assertEqual(skipped, {"excluded_directories": 1, "generated": 1, "symlinks": 1, "submodules": 1})
        self.assertEqual(download.call_args.args[:2], ("o/r", "deadbeef"))
        self.assertEqual(download.call_args.args[2][0][0].as_posix(), "src/main file.cs")

    @patch("discovery.pilot.fetch_source_batch", return_value=[b"{}"])
    @patch("discovery.pilot.subprocess.run")
    def test_file_limit_prioritizes_manifests_and_marks_partial(self, run, download):
        run.return_value.returncode = 0
        run.return_value.stdout = self.tree([
            ("a.cs", 2, "100644"), ("package.json", 2, "100644"),
        ], truncated=True)
        with tempfile.TemporaryDirectory() as directory, patch("discovery.pilot.MAX_SELECTED_FILES", 1):
            with self.assertLogs("pilot", level="WARNING"):
                files, skipped = selected_sources("o/r", "sha", Path(directory))
        self.assertEqual(files, [("package.json", "{}")])
        self.assertEqual(skipped["selected_file_limit"], 1)
        self.assertEqual(skipped["truncated_tree"], 1)
        self.assertTrue(PARTIAL_REASONS.intersection(skipped))
        self.assertEqual(download.call_count, 1)

    @patch("discovery.pilot.fetch_source_batch", return_value=[b"code"])
    @patch("discovery.pilot.subprocess.run")
    def test_oversize_and_total_byte_limits_preserved(self, run, download):
        run.return_value.returncode = 0
        run.return_value.stdout = self.tree([
            ("a.cs", 4, "100644"), ("b.cs", 4, "100644"),
            ("big.cs", 10000000, "100644"),
        ])
        with tempfile.TemporaryDirectory() as directory, patch("discovery.pilot.MAX_EXTRACTED", 4):
            files, skipped = selected_sources("o/r", "sha", Path(directory))
        self.assertEqual(len(files), 1)
        self.assertEqual(skipped["extraction_limit"], 1)
        self.assertEqual(skipped["oversize_files"], 1)
        self.assertEqual(download.call_count, 1)

    @patch("discovery.pilot.fetch_source_batch")
    @patch("discovery.pilot.subprocess.run")
    def test_unsafe_tree_path_rejected_before_any_download(self, run, download):
        run.return_value.returncode = 0
        run.return_value.stdout = self.tree([("../escape.cs", 4, "100644")])
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(PilotError):
            selected_sources("o/r", "sha", Path(directory))
        download.assert_not_called()

    @patch("discovery.pilot.download")
    @patch("discovery.pilot.graphql")
    def test_graphql_blob_batch_preserves_exact_text(self, api, raw):
        api.return_value = {"repository": {
            "b0": {"text": "code", "isBinary": False, "isTruncated": False, "byteSize": 4},
        }}
        result = fetch_source_batch("o/r", "commit", [(Path("main.cs"), 4, "a" * 40)])
        self.assertEqual(result, [b"code"])
        self.assertEqual(api.call_args.kwargs["oid0"], "a" * 40)
        self.assertIn("$oid0:GitObjectID!", api.call_args.args[0])
        raw.assert_not_called()

    @patch("discovery.pilot.download", return_value=b"\xff\xfeA\x00")
    @patch("discovery.pilot.graphql")
    def test_truncated_or_transcoded_blob_uses_pinned_raw_source(self, api, raw):
        api.return_value = {"repository": {
            "b0": {"text": None, "isBinary": True, "isTruncated": False, "byteSize": 4},
        }}
        result = fetch_source_batch("o/r", "commit", [(Path("main file.cs"), 4, "a" * 40)])
        self.assertEqual(result, [b"\xff\xfeA\x00"])
        raw.assert_called_once_with("https://raw.githubusercontent.com/o/r/commit/main%20file.cs", MAX_FILE)

    @patch("discovery.pilot.graphql", return_value={"repository": {"b0": None}})
    def test_missing_pinned_blob_fails_explicitly(self, api):
        with self.assertRaisesRegex(PilotError, "Pinned source blob is missing"):
            fetch_source_batch("o/r", "commit", [(Path("main.cs"), 4, "a" * 40)])

    @patch("discovery.pilot.fetch_source_batch")
    @patch("discovery.pilot.subprocess.run")
    def test_batches_bound_query_count_without_omitting_source(self, run, fetch):
        run.return_value.returncode = 0
        run.return_value.stdout = self.tree([(f"src/f{i}.cs", 4, "100644") for i in range(41)])
        fetch.side_effect = lambda repo, sha, entries: [b"code" for _ in entries]
        with tempfile.TemporaryDirectory() as directory:
            files, skipped = selected_sources("o/r", "commit", Path(directory))
        self.assertEqual(len(files), 41)
        self.assertEqual(skipped, {})
        self.assertEqual([len(call.args[2]) for call in fetch.call_args_list], [40, 1])


class RepositoryPolicyTests(unittest.TestCase):
    def metadata(self):
        return {"repository": {
            "id": "R_1", "nameWithOwner": "o/r", "url": "https://github.com/o/r",
            "isPrivate": False, "isFork": False, "isArchived": False,
            "primaryLanguage": {"name": "C#"},
            "languages": {"edges": [], "pageInfo": {"hasNextPage": False}},
            "defaultBranchRef": {"target": {"oid": "current-sha"}},
        }}

    @patch("discovery.pilot.acquire_sources")
    @patch("discovery.pilot.graphql")
    def test_rerun_preserves_recorded_sha(self, api, acquire):
        api.return_value = self.metadata()
        acquire.return_value = ([("main.cs", "class Main {}")], {}, "selected-files")
        with tempfile.TemporaryDirectory() as directory:
            record = analyze_repository({"name": "o/r", "sha": "original-sha"},
                                        Path("inspector"), Path(directory))
        self.assertEqual(acquire.call_args.args[:2], ("o/r", "original-sha"))
        self.assertEqual(record["sha"], "original-sha")
        self.assertEqual(record["source_method"], "selected-files")

    @patch("discovery.pilot.acquire_sources")
    @patch("discovery.pilot.graphql")
    def test_all_incomplete_retrieval_reasons_are_partial(self, api, acquire):
        api.return_value = self.metadata()
        for reason in PARTIAL_REASONS:
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                acquire.return_value = ([("main.cs", "class Main {}")], {reason: 1}, "selected-files")
                record = analyze_repository({"name": "o/r"}, Path("inspector"), Path(directory))
                self.assertEqual(record["status"], "partial")
        for reason in ("symlinks", "submodules", "generated"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                acquire.return_value = ([("main.cs", "class Main {}")], {reason: 1}, "archive")
                record = analyze_repository({"name": "o/r"}, Path("inspector"), Path(directory))
                self.assertEqual(record["status"], "success")

    @patch("discovery.pilot.acquire_sources")
    @patch("discovery.pilot.graphql")
    def test_private_repository_is_not_rescanned(self, api, acquire):
        metadata = self.metadata()
        metadata["repository"]["isPrivate"] = True
        api.return_value = metadata
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(PilotError, "no longer public"):
            analyze_repository({"name": "o/r"}, Path("inspector"), Path(directory))
        acquire.assert_not_called()

    @patch("discovery.pilot.acquire_sources", return_value=([], {"unsupported_extensions": 1}, "archive"))
    @patch("discovery.pilot.graphql")
    def test_no_source_is_not_counted_as_complete_or_failed(self, api, acquire):
        api.return_value = self.metadata()
        with tempfile.TemporaryDirectory() as directory:
            record = analyze_repository({"name": "o/r"}, Path("inspector"), Path(directory))
        self.assertEqual(record["status"], "not_applicable")
        metrics = aggregate([record])
        self.assertEqual(metrics["successful"], 0)
        self.assertEqual(metrics["failed"], 0)
        self.assertEqual(metrics["not_applicable"], 1)

    @patch("discovery.pilot.inspect_sources")
    @patch("discovery.pilot.acquire_sources", return_value=(
        [("main.cpp", "#include <windows.h>")], {}, "archive",
    ))
    @patch("discovery.pilot.graphql")
    def test_incomplete_inspector_preserves_findings_but_stays_partial(self, api, acquire, inspector):
        api.return_value = self.metadata()
        inspector.return_value = {
            "components": ["Win32"], "frameworks": [], "evidence": [],
            "incomplete": {"filesSkipped": 1},
        }
        with tempfile.TemporaryDirectory() as directory:
            record = analyze_repository({"name": "o/r"}, Path("inspector"), Path(directory))
        self.assertEqual(record["status"], "partial")
        self.assertEqual(record["components"], ["Win32"])
        self.assertEqual(record["windows_scan"], "partial")

    @patch("discovery.pilot.inspect_sources", return_value={
        "components": ["Win32"], "frameworks": [], "evidence": [], "incomplete": {},
    })
    @patch("discovery.pilot.acquire_sources", return_value=(
        [("main.cpp", "#include <windows.h>")], {}, "archive",
    ))
    @patch("discovery.pilot.graphql")
    def test_windows_cache_revalidates_inspector_strategy(self, api, acquire, inspector):
        api.return_value = self.metadata()
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            analyze_repository({"name": "o/r"}, Path("inspector"), cache)
            cached = next(cache.glob("*.json"))
            previous = json.loads(cached.read_text())
            previous.pop("inspector_strategy")
            cached.write_text(json.dumps(previous))
            analyze_repository({"name": "o/r"}, Path("inspector"), cache)
            analyze_repository({"name": "o/r"}, Path("inspector"), cache)
        self.assertEqual(acquire.call_count, 2)
        self.assertEqual(inspector.call_count, 2)


class ClassificationTests(unittest.TestCase):
    def test_winforms_application(self):
        result = classify([
            ("app.csproj", "<Project><OutputType>WinExe</OutputType><UseWindowsForms>true</UseWindowsForms></Project>"),
            ("Program.cs", "using System.Windows.Forms;\nclass App {}"),
        ])
        self.assertEqual(result["purpose"], "Application")
        self.assertIn("Windows", result["platforms"])
        self.assertIn("Windows Forms", result["frameworks"])
        self.assertEqual(result["evidence"][0]["line"], 1)

    def test_csharp_alone_does_not_imply_windows_or_application(self):
        result = classify([("Library.cs", "public class Library {}")])
        self.assertEqual(result["platforms"], ["Unknown"])
        self.assertNotEqual(result["purpose"], "Application")

    def test_multiple_platforms_and_frameworks(self):
        result = classify([
            ("app.csproj", "<TargetFrameworks>net8.0-windows;net8.0-android;net8.0-ios</TargetFrameworks><UseMaui>true</UseMaui>"),
        ])
        self.assertEqual(set(result["os_targets"]), {"Windows", "Android", "iOS"})
        self.assertIn(".NET runtime (OS unspecified)", result["platforms"])
        self.assertIn(".NET MAUI", result["frameworks"])

    def test_electron_requires_app_and_windows_evidence(self):
        result = classify([("package.json", '{"main":"app.js","devDependencies":{"electron":"1"}}'),
                           ("windows/icon.json", "{}")])
        self.assertEqual(result["purpose"], "Application")
        self.assertIn("Windows", result["platforms"])
        self.assertIn("Electron", result["frameworks"])

    def test_invalid_package_manifest_is_logged(self):
        with self.assertLogs("pilot", level="WARNING") as logs:
            result = classify([("package.json", "{broken")])
        self.assertIn("Invalid package manifest", logs.output[0])
        self.assertNotEqual(result["purpose"], "Application")

    def test_invalid_package_dependency_shape_fails_explicitly(self):
        with self.assertRaisesRegex(PilotError, "dependencies are not objects"):
            classify([("package.json", '{"main":"main.js","dependencies":["electron"]}')])

    def test_component_shapes_are_not_forced_to_sum_to_100(self):
        def record(components, **overrides):
            return {
                "status": "success", "platforms": ["Windows"], "frameworks": ["WPF"],
                "os_targets": ["Windows"],
                "primary_language": "C#", "purpose": "Application", "windows_scan": "success",
                "application_types": ["WPF"], "components": components, **overrides,
            }
        records = [record(["Win32", "COM"]), record(["COM"]), record(["Win32"], status="partial"),
                   {"status": "failed"}, record(["Win32"], purpose="Unknown / library or tool")]
        metrics = aggregate(records)
        components = {r["label"]: r for r in metrics["components"]}
        self.assertEqual(metrics["windows_applications"], 2)
        self.assertEqual(components["Win32"]["percent"], 50)
        self.assertEqual(components["COM"]["percent"], 100)
        self.assertEqual(components["COM"]["denominator"], 2)
        self.assertEqual(metrics["successful"], 3)
        candidates = {r["label"]: r for r in metrics["candidate_components"]}
        self.assertEqual(candidates["Win32"]["denominator"], 3)
        self.assertEqual(candidates["Win32"]["count"], 2)

    def test_requested_example_thresholds(self):
        records = []
        for i in range(100):
            records.append({
                "status": "success", "platforms": ["Windows"], "frameworks": ["WPF"],
                "os_targets": ["Windows"],
                "primary_language": "C#", "purpose": "Application", "windows_scan": "success",
                "application_types": ["WPF"],
                "components": (["Win32"] if i < 32 else []) + (["COM"] if i < 51 else []),
            })
        result = {r["label"]: r for r in aggregate(records)["components"]}
        self.assertEqual(result["Win32"]["percent"], 32)
        self.assertEqual(result["COM"]["percent"], 51)

    def test_empty_denominator_is_null_not_zero(self):
        metrics = aggregate([])
        self.assertTrue(all(r["percent"] is None for r in metrics["components"]))

    def test_application_types_preserve_overlap(self):
        self.assertEqual(application_types(["WPF", "Windows Forms"], ["COM"]), ["WPF", "Windows Forms"])

    def test_environment_does_not_imply_supported_operating_system(self):
        cases = [
            ("main.py", "import argparse", "Python runtime (OS unspecified)"),
            ("run.ps1", "Get-Process", "Shell / automation (OS unspecified)"),
            ("infra/main.tf", 'resource "aws_s3_bucket" "logs" {}', "Cloud / infrastructure"),
            ("Dockerfile", "FROM python:3.11", "Containers / Kubernetes"),
            ("go.mod", "module example.org/tool", "Native code (OS unspecified)"),
            ("package.json", '{"dependencies":{"express":"1"}}', "Server / backend"),
            ("index.html", "<!doctype html><title>App</title>", "Web"),
            ("contract.rs", "use soroban_sdk;", "Smart contracts"),
        ]
        for path, text, label in cases:
            with self.subTest(label=label):
                result = classify([(path, text)])
                self.assertIn(label, result["platforms"])
                self.assertEqual(result["os_targets"], ["Unspecified"])
                self.assertTrue(any(e["label"] == label for e in result["evidence"]))

    def test_runtime_evidence_is_file_scoped(self):
        result = classify([("settings.yml", 'description: package.json\nexample: "import argparse"')])
        self.assertEqual(result["platforms"], ["Unknown"])


if __name__ == "__main__":
    unittest.main()
