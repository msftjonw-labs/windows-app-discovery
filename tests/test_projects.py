import json
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import Mock, patch

from discovery import pilot, semgrep
from discovery.projects import classify_projects, metadata, powershell


def projects(files, supplemental=()):
    return classify_projects(files, pilot.classify, supplemental)


def repository():
    return {"id": "R1", "nameWithOwner": "o/r", "url": "https://github.com/o/r",
            "isPrivate": False, "isFork": False, "isArchived": False,
            "primaryLanguage": {"name": "PowerShell"},
            "languages": {"edges": [], "pageInfo": {"hasNextPage": False}},
            "defaultBranchRef": {"target": {"oid": "sha"}}}


class ProjectTests(unittest.TestCase):
    def test_mixed_projects_do_not_leak_frameworks_or_service_labels(self):
        result = projects([
            ("desktop/App.csproj", "<Project><PropertyGroup><UseWPF>true</UseWPF><OutputType>WinExe</OutputType></PropertyGroup></Project>"),
            ("desktop/App.cs", "using System.Windows.Controls;"),
            ("service/Worker.csproj", "<Project/>"),
            ("service/Program.cs", "builder.UseWindowsService();"),
            ("scripts/install.ps1", "Get-Service foo\nNew-Service -Name foo -BinaryPathName 'worker.exe'"),
            ("scripts/run.ps1", "Get-Process"),
        ])
        by_path = {p["path"]: p for p in result}
        self.assertIn("WPF", by_path["desktop/App.csproj"]["labels"])
        self.assertNotIn("Windows service", by_path["desktop/App.csproj"]["labels"])
        self.assertEqual(by_path["service/Worker.csproj"]["labels"], ["Windows service"])
        inventory = next(p for p in result if p["kind"] == "unassigned")
        self.assertIn("PowerShell install script", inventory["labels"])
        self.assertIn("Service management", inventory["labels"])
        self.assertNotIn("PowerShell-backed service", inventory["labels"])
        for project in result:
            self.assertIn(project["confidence"], {"low", "medium", "high"})
            for item in project["evidence"]:
                self.assertIn(item["path"], project["files"])
                self.assertGreaterEqual(item["line"], 1)
                self.assertIn(item["confidence"], {"low", "medium", "high"})

    def test_nested_project_wins_over_outer_project(self):
        result = projects([
            ("package.json", "{}"), ("nested/App.csproj", "<Project/>"),
            ("nested/Program.cs", "builder.UseWindowsService();"),
            ("main.js", "console.log('hi')")])
        by_path = {p["path"]: p for p in result}
        self.assertNotIn("Windows service", by_path["package.json"]["labels"])
        self.assertIn("Windows service", by_path["nested/App.csproj"]["labels"])
        self.assertNotIn("nested/Program.cs", by_path["package.json"]["files"])

    def test_go_mod_survives_extraction_and_defines_nested_boundary(self):
        content = io.BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            for path, text in [("package.json", "{}"), ("nested/go.mod", "module example.org/nested"),
                               ("nested/main.go", "package main\nfunc main() {}")]:
                archive.writestr("root/" + path, text)
        with tempfile.TemporaryDirectory() as folder:
            files, skipped = pilot.extract_sources(content.getvalue(), Path(folder))
        self.assertIn("nested/go.mod", dict(files))
        self.assertEqual(skipped, {})
        self.assertIsNone(pilot.source_exclusion(Path("nested/go.mod")))
        self.assertEqual(pilot.source_exclusion(Path("nested/other.mod")), "unsupported_extensions")
        result = {project["path"]: project for project in projects(files)}
        self.assertIn("nested/main.go", result["nested/go.mod"]["files"])
        self.assertNotIn("nested/main.go", result["package.json"]["files"])

    def test_same_directory_projects_have_explicit_ambiguous_files(self):
        result = projects([("A.csproj", "<Project/>"), ("B.csproj", "<Project/>"),
                           ("Program.cs", "System.Windows.Forms")])
        ambiguous = next(p for p in result if p["kind"] == "ambiguous")
        self.assertIn("Windows Forms", ambiguous["labels"])
        self.assertTrue(all("Windows Forms" not in p["labels"] for p in result if p["kind"] == "MSBuild"))

    def test_shared_build_metadata_not_propagated(self):
        result = projects([("App.csproj", "<Project/>"),
                           ("Directory.Build.props", "<Project><UseWPF>true</UseWPF></Project>")])
        shared = next(p for p in result if p["kind"] == "shared")
        self.assertEqual(shared["labels"], ["WPF"])
        self.assertEqual(next(p for p in result if p["kind"] == "MSBuild")["labels"], [])

    def test_powershell_module_manifest_and_code_are_associated(self):
        result = projects([("module/Example.psd1", "@{ RootModule = 'Example.psm1' }"),
                           ("module/Example.psm1", "function Invoke-Example {}")])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["kind"], "PowerShell module")
        self.assertEqual(result[0]["labels"], ["PowerShell module"])

    def test_management_namespace_is_not_service_implementation(self):
        result = projects([("A.csproj", "<Project/>"),
                           ("Manage.cs", "using System.ServiceProcess;\nServiceController.GetServices();")])
        self.assertIn("Service management", result[0]["labels"])
        self.assertNotIn("Windows service", result[0]["labels"])

    def test_conditional_metadata_is_low_confidence_and_never_evaluated(self):
        findings, notes = metadata("A.csproj", """<Project xmlns="urn:msbuild">
<PropertyGroup Condition="'$(OS)' == 'Windows_NT'">
<UseWPF>true</UseWPF>
</PropertyGroup><Import Project="untrusted.targets"/></Project>""")
        self.assertEqual(findings[0]["label"], "WPF")
        self.assertEqual(findings[0]["line"], 3)
        self.assertEqual(findings[0]["confidence"], "low")
        self.assertTrue(findings[0]["conditional"])
        self.assertIn("MSBuild imports are not evaluated", notes)

    def test_metadata_conditions_repeated_lines_and_false_values(self):
        findings, _ = metadata("A.csproj", """<Project>
<!-- <UseWPF>true</UseWPF> -->
<UseWPF>false</UseWPF>
<UseWPF Condition="false">true</UseWPF>
<UseWindowsForms>true</UseWindowsForms>
</Project>""")
        self.assertEqual([(e["label"], e["line"], e["confidence"]) for e in findings],
                         [("WPF", 4, "low"), ("Windows Forms", 5, "medium")])

    def test_malformed_and_entity_xml_cannot_create_project_findings(self):
        for xml in ("<Project><UseWPF>true", '<!DOCTYPE Project [<!ENTITY x "true">]><Project><UseWPF>&x;</UseWPF></Project>'):
            with self.subTest(xml=xml):
                result = projects([("A.csproj", xml)])
                self.assertEqual(result[0]["labels"], [])
                self.assertTrue(result[0]["notes"])

    def test_multitarget_metadata_and_literal_executable(self):
        findings, _ = metadata("A.csproj", "<Project><TargetFrameworks>net8.0;net8.0-windows</TargetFrameworks><OutputType>Exe</OutputType></Project>")
        self.assertEqual({e["label"] for e in findings}, {"Windows target", "Executable"})

    def test_deep_metadata_does_not_recurse(self):
        text = "<Project>" + "<PropertyGroup>" * 1500 + "<UseWPF>true</UseWPF>" + "</PropertyGroup>" * 1500 + "</Project>"
        findings, _ = metadata("App.csproj", text)
        self.assertEqual(findings[0]["label"], "WPF")

    def test_supplemental_xml_cannot_override_safe_metadata(self):
        for text, labels in [
                ('<Project><UseWPF Condition="false">true</UseWPF></Project>', ["WPF"]),
                ("<Project><!-- <UseWPF>true</UseWPF> --></Project>", []),
                ("<Project><UseWPF>true", [])]:
            with self.subTest(text=text):
                result = projects([("App.csproj", text)], [{
                    "path": "App.csproj", "line": 1, "label": "WPF", "engine": "Application Inspector"}])
                self.assertEqual(result[0]["labels"], labels)
                if labels:
                    self.assertEqual(result[0]["label_confidence"]["WPF"], "low")
                    self.assertEqual(result[0]["confidence"], "low")

    def test_add_windows_service_is_service_host_evidence(self):
        result = projects([("App.csproj", "<Project/>"),
                           ("Program.cs", "builder.Services.AddWindowsService();")])
        self.assertIn("Windows service", result[0]["labels"])
        self.assertIn("Windows", pilot.classify([("Program.cs", "builder.Services.AddWindowsService();")])["platforms"])

    def test_safe_avalonia_package_metadata_and_conditional_confidence(self):
        for package in ("Avalonia", "Avalonia.Desktop"):
            for condition, confidence in [("", "medium"), (' Condition="false"', "low")]:
                with self.subTest(package=package, condition=condition):
                    text = f'<Project><ItemGroup{condition}><PackageReference Include="{package}" Version="1"/></ItemGroup></Project>'
                    result = projects([("App.csproj", text)], [{
                        "path": "App.csproj", "line": 1, "label": "Avalonia", "engine": "Application Inspector"}])
                    self.assertEqual(result[0]["labels"], ["Cross-platform: Avalonia"])
                    self.assertEqual(result[0]["label_confidence"]["Cross-platform: Avalonia"], confidence)

    def test_powershell_is_not_windows_and_management_is_not_host(self):
        for text in ("Get-Process", "Get-Service foo", "Start-Service foo",
                     "New-Service -BinaryPathName 'worker.exe'"):
            with self.subTest(text=text):
                self.assertNotIn("Windows", pilot.classify([("run.ps1", text)])["platforms"])
                self.assertNotIn("PowerShell-backed service", [e["label"] for e in powershell("run.ps1", text)])

    def test_registration_is_not_proof_of_a_working_service_host(self):
        text = "\nNew-Service -Name Foo -BinaryPathName 'pwsh.exe -File ./worker.ps1'"
        findings = powershell("install.ps1", text)
        host = next(e for e in findings if e["label"] == "PowerShell service registration")
        self.assertEqual(host["confidence"], "low")
        self.assertEqual(host["line"], 2)
        self.assertIn("lifecycle", host["note"])
        self.assertNotIn("PowerShell-backed service", [e["label"] for e in findings])
        self.assertNotIn("PowerShell-backed service", [e["label"] for e in powershell("service.ps1", "while ($true) { Get-Process }")])

    def test_service_wrapper_requires_powershell_payload(self):
        findings = powershell("install.ps1", 'nssm install worker powershell.exe -File worker.ps1')
        self.assertIn("PowerShell-backed service", [e["label"] for e in findings])
        findings = powershell("install.ps1", 'nssm install worker worker.exe')
        self.assertNotIn("PowerShell-backed service", [e["label"] for e in findings])
        findings = projects([("worker.xml", '<service><executable>pwsh.exe</executable><arguments>-File worker.ps1</arguments></service>')])
        self.assertIn("PowerShell-backed service", findings[0]["labels"])

    def test_embedded_powershell_host_alone_is_not_service_evidence(self):
        result = projects([("App.csproj", "<Project/>"), ("Program.cs", "using System.Management.Automation;")],
                          [{"path": "Program.cs", "line": 1, "rule": "pilot-powershell-host",
                            "label": "PowerShell host", "confidence": "medium", "engine": "Semgrep"}])
        self.assertIn("PowerShell host", result[0]["labels"])
        self.assertNotIn("PowerShell-backed service", result[0]["labels"])

    def test_comments_do_not_create_service_registration(self):
        text = "# New-Service -BinaryPathName 'pwsh -File worker.ps1'\n<#\nNew-Service -BinaryPathName 'pwsh -File worker.ps1'\n#>\nGet-Process # nssm install worker pwsh -File worker.ps1"
        self.assertEqual([e["label"] for e in powershell("run.ps1", text)], ["PowerShell script"])

    def test_multiple_labels_and_inspector_attribution(self):
        result = projects([("App.csproj", "<Project><UseWPF>true</UseWPF></Project>"),
                           ("Program.cs", "builder.UseWindowsService();")],
                          [{"path": "Program.cs", "line": 1, "rule": "PILOT_service",
                            "label": "Windows services", "engine": "Application Inspector"}])
        self.assertIn("WPF", result[0]["labels"])
        self.assertIn("Windows service", result[0]["labels"])
        self.assertTrue(any(e["engine"] == "Application Inspector" for e in result[0]["evidence"]))


class SemgrepTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)
        self.source = self.work / "source"
        self.source.mkdir()
        (self.source / "Program.cs").write_text("builder.UseWindowsService();\n", encoding="utf-8")
        self.files = [("Program.cs", "builder.UseWindowsService();\n")]
        self.executable = self.work / "semgrep"
        self.executable.write_text("launcher", encoding="utf-8")

    def result(self, path=None, line=1, rule="pilot-windows-service"):
        return {"path": str(path or self.source / "Program.cs"), "start": {"line": line}, "check_id": rule}

    def scan(self, report):
        with patch("discovery.semgrep.subprocess.run", side_effect=[
                Mock(returncode=0, stdout="1.2.3"), Mock(returncode=0, stdout=json.dumps(report))]) as run:
            result = semgrep.scan(self.source, self.executable, self.work, self.files)
        return result, run

    def test_disabled_never_invokes_engine(self):
        with patch("discovery.semgrep.subprocess.run") as run:
            self.assertEqual(semgrep.scan(self.source, None, self.work, [])["status"], "disabled")
            self.assertEqual(semgrep.identity(None)["status"], "disabled")
            run.assert_not_called()

    def test_local_rules_and_isolation_controls(self):
        result, run = self.scan({"results": [self.result()], "errors": []})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["evidence"][0]["path"], "Program.cs")
        command = run.call_args.args[0]
        self.assertIn("--metrics=off", command)
        self.assertIn("--disable-version-check", command)
        self.assertIn("--oss-only", command)
        self.assertNotIn("--config=auto", command)
        config = Path(command[command.index("--config") + 1])
        self.assertEqual(json.loads(config.read_text())["rules"], semgrep.RULES)
        self.assertEqual(run.call_args.kwargs["cwd"], self.work)
        self.assertEqual(run.call_args.kwargs["timeout"], 90)
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["SEMGREP_SEND_METRICS"], "off")
        self.assertEqual(env["SEMGREP_ENABLE_VERSION_CHECK"], "0")
        self.assertEqual(env["SEMGREP_APP_TOKEN"], "")
        self.assertEqual(env["SEMGREP_SETTINGS_FILE"], str(self.work / "semgrep-settings.yml"))

    def test_timeout_and_missing_engine_are_supplemental_failures(self):
        for error, status in [(subprocess.TimeoutExpired("semgrep", 90), "partial"),
                              (FileNotFoundError("missing"), "unavailable")]:
            with self.subTest(error=error), patch("discovery.semgrep.subprocess.run", side_effect=error):
                result = semgrep.scan(self.source, self.executable, self.work, self.files)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["evidence"], [])

    def test_engine_exit_and_invalid_json(self):
        for output, code, expected in [("{}", 2, "partial"), ("not json", 0, "unavailable"),
                                       ("{}", 0, "unavailable")]:
            with self.subTest(output=output, code=code), patch("discovery.semgrep.subprocess.run", side_effect=[
                    Mock(returncode=0, stdout="1"), Mock(returncode=code, stdout=output)]):
                self.assertEqual(semgrep.scan(self.source, self.executable, self.work, [])["status"], expected)

    def test_invalid_paths_rules_and_lines_are_rejected(self):
        bad = [self.result(self.work / "outside.cs"), self.result("source/../source/Program.cs"),
               self.result(self.source / "missing.cs"),
               self.result(line=0), self.result(line=True), self.result(line=999),
               self.result(rule="untrusted-rule")]
        if os.name != "nt":
            bad.append(self.result("source\\Program.cs"))
        result, _ = self.scan({"results": bad + [self.result("source/Program.cs")], "errors": []})
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["rejected_findings"], len(bad))
        self.assertEqual(len(result["evidence"]), 1)

    def test_symlink_outside_source_is_rejected(self):
        outside = self.work / "outside.cs"
        outside.write_text("untrusted")
        try:
            (self.source / "link.cs").symlink_to(outside)
        except OSError:
            self.skipTest("Symlinks unavailable")
        self.files.append(("link.cs", "untrusted"))
        result, _ = self.scan({"results": [self.result(self.source / "link.cs")]})
        self.assertEqual(result["rejected_findings"], 1)

    def test_engine_errors_mark_supplement_partial(self):
        result, _ = self.scan({"results": [self.result()], "errors": [{"message": "timeout"}]})
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["evidence"]), 1)

    def test_structural_rules_refine_confidence_not_generic_text_matches(self):
        result, _ = self.scan({"results": [
            self.result(rule="pilot-windows-service"),
            self.result(rule="pilot-csharp-service-host"),
            self.result(rule="pilot-csharp-winforms"),
            self.result(rule="pilot-csharp-powershell-host"),
        ], "errors": []})
        self.assertEqual(result["evidence"][0]["confidence"], "medium")
        self.assertTrue(all(item["confidence"] == "high" for item in result["evidence"][1:]))
        refined = projects([("App.csproj", "<Project/>"), *self.files], result["evidence"])
        self.assertEqual(refined[0]["label_confidence"]["Windows service"], "high")
        self.assertEqual(refined[0]["label_confidence"]["Windows Forms"], "high")
        self.assertEqual(refined[0]["label_confidence"]["PowerShell host"], "high")
        self.assertNotIn("PowerShell-backed service", refined[0]["labels"])

    def test_structural_rules_use_csharp_ast_patterns_and_both_host_apis(self):
        structural = {rule["id"]: rule for rule in semgrep.RULES if rule["id"] in semgrep.STRUCTURAL_RULES}
        self.assertEqual(len(structural), 3)
        for rule in structural.values():
            self.assertEqual(rule["languages"], ["csharp"])
            self.assertIn("pattern-either", rule)
            self.assertNotIn("pattern-regex", rule)
        forms = structural["pilot-csharp-winforms"]["pattern-either"]
        self.assertIn("class $FORM : System.Windows.Forms.Form", forms[0]["pattern"])
        self.assertEqual(forms[1]["patterns"][0]["pattern-inside"], "using System.Windows.Forms;\n...")
        calls = structural["pilot-csharp-service-host"]["pattern-either"]
        self.assertEqual({item["pattern"] for item in calls},
                         {"$HOST.UseWindowsService(...)", "$SERVICES.AddWindowsService(...)"})
        host = structural["pilot-csharp-powershell-host"]["pattern-either"]
        self.assertEqual(host[0]["pattern"], "System.Management.Automation.PowerShell.Create(...)")

    def test_identity_changes_with_engine_version_and_launcher(self):
        with patch("discovery.semgrep.subprocess.run", return_value=Mock(returncode=0, stdout="1")):
            first = semgrep.identity(self.executable, self.work)
            self.executable.write_text("replacement")
            second = semgrep.identity(self.executable, self.work)
        with patch("discovery.semgrep.subprocess.run", return_value=Mock(returncode=0, stdout="2")):
            third = semgrep.identity(self.executable, self.work)
        self.assertNotEqual(first, second)
        self.assertNotEqual(second, third)


class RepositoryIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.cache = Path(self.directory.name)
        self.repo = patch("discovery.pilot.resolve_repository", return_value=repository())
        self.repo.start()
        self.addCleanup(self.repo.stop)

    def test_nonwindows_powershell_application_types_and_projects(self):
        with patch("discovery.pilot.acquire_sources", return_value=(
                [("scripts/run.ps1", "Get-Process")], {}, "archive")), patch("discovery.pilot.inspect_sources") as inspector:
            record = pilot.analyze_repository({"name": "o/r"}, Path("inspector"), self.cache)
        inspector.assert_not_called()
        self.assertEqual(record["status"], "success")
        self.assertEqual(record["windows_scan"], "not_applicable")
        self.assertIn("PowerShell script", record["application_types"])
        self.assertNotIn("Windows", record["platforms"])
        self.assertEqual(record["semgrep"]["status"], "disabled")
        self.assertTrue(record["projects"])

    def test_failed_supplement_does_not_invalidate_inspector(self):
        with patch("discovery.pilot.acquire_sources", return_value=(
                [("App.csproj", "<Project><UseWPF>true</UseWPF></Project>")], {}, "archive")), \
                patch("discovery.pilot.inspect_sources", return_value={
                    "components": ["COM"], "frameworks": ["WPF"], "evidence": [], "incomplete": {}}) as inspector, \
                patch("discovery.pilot.semgrep_engine.identity", return_value={"status": "configured", "version": "1"}), \
                patch("discovery.pilot.semgrep_engine.scan", return_value={"status": "partial", "reason": "timeout", "evidence": []}):
            record = pilot.analyze_repository({"name": "o/r"}, Path("inspector"), self.cache, Path("semgrep"))
        inspector.assert_called_once()
        self.assertEqual(record["status"], "success")
        self.assertEqual(record["windows_scan"], "success")
        self.assertEqual(record["components"], ["COM"])
        self.assertEqual(record["semgrep"]["status"], "partial")

    def test_inspector_service_component_does_not_make_management_utility_a_service(self):
        for source, is_host in [
                ("using System.ServiceProcess;\nServiceController.GetServices();", False),
                ("builder.UseWindowsService();", True),
                ("builder.Services.AddWindowsService();", True),
                ("ServiceBase.Run(new Worker());", True),
                ("StartServiceCtrlDispatcherW(table);", True)]:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as folder, \
                    patch("discovery.pilot.acquire_sources", return_value=([
                        ("App.csproj", "<Project><OutputType>Exe</OutputType></Project>"),
                        ("Program.cs", source)], {}, "archive")), \
                    patch("discovery.pilot.inspect_sources", return_value={
                        "components": ["Windows services"], "frameworks": [], "evidence": [],
                        "incomplete": {}}):
                record = pilot.analyze_repository({"name": "o/r"}, Path("inspector"), Path(folder))
                self.assertIn("Windows services", record["components"])
                self.assertEqual("Windows service" in record["application_types"], is_host)
                self.assertEqual("Windows service" in record["projects"][0]["labels"], is_host)

    def test_cache_separates_disabled_configured_and_engine_versions(self):
        with patch("discovery.pilot.acquire_sources", return_value=(
                [("run.ps1", "Get-Process")], {}, "archive")) as acquire, \
                patch("discovery.pilot.semgrep_engine.identity", side_effect=[
                    {"status": "disabled"}, {"status": "configured", "version": "1"},
                    {"status": "configured", "version": "1"}, {"status": "configured", "version": "2"}]), \
                patch("discovery.pilot.semgrep_engine.scan", return_value={"status": "success", "evidence": []}) as scan:
            pilot.analyze_repository({"name": "o/r"}, Path("inspector"), self.cache)
            for _ in range(3):
                pilot.analyze_repository({"name": "o/r"}, Path("inspector"), self.cache, Path("semgrep"))
        self.assertEqual(acquire.call_count, 3)
        self.assertEqual(scan.call_count, 3)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 3)

    def test_partial_supplement_cache_retries(self):
        with patch("discovery.pilot.acquire_sources", return_value=(
                [("run.ps1", "Get-Process")], {}, "archive")) as acquire, \
                patch("discovery.pilot.semgrep_engine.identity", return_value={"status": "configured"}), \
                patch("discovery.pilot.semgrep_engine.scan", return_value={"status": "partial", "evidence": []}):
            for _ in range(2):
                pilot.analyze_repository({"name": "o/r"}, Path("inspector"), self.cache, Path("semgrep"))
        self.assertEqual(acquire.call_count, 2)


if __name__ == "__main__":
    unittest.main()
