"""Conservative project attribution; confidence describes evidence, not probability.

MSBuild conditions/imports/globs are never evaluated. Shared and ambiguous sources
remain explicit inventory entries instead of being attributed to every project.
"""

import json
import logging
from pathlib import PurePosixPath
import re
import tomllib
import xml.etree.ElementTree as ET

PROJECT_SUFFIXES = {".csproj", ".vbproj", ".fsproj", ".vcxproj", ".psd1"}
PROJECT_NAMES = {"package.json", "pyproject.toml", "cargo.toml", "go.mod",
                 "cmakelists.txt", "pom.xml", "pubspec.yaml", "build.gradle", "build.gradle.kts"}
XML_SUFFIXES = {".csproj", ".vbproj", ".fsproj", ".vcxproj", ".props", ".targets"}
DESKTOP = {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP"}
RANK = {"low": 0, "medium": 1, "high": 2}
APPLICATION_TYPES = {
    "Web frontend", "Backend / API", "Command-line tool", "Library / SDK",
    "Shell / batch automation", "Build automation", "Infrastructure as code",
    "Container / orchestration configuration", "Notebook / data analysis",
    "Mobile app", "macOS app", "Native desktop app", "Embedded / firmware",
    "Smart contract", "Python application / script", "Executable application",
}
TYPE_RULES = [
    ("web-ui", "Web frontend", r"\.(?:jsx|tsx|vue|svelte|astro|html?)$",
     r"<(?:html|div|main|body)\b|</[A-Za-z][\w.]*\s*>|<[A-Z][\w.]*\b[^>\n]*/>"),
    ("backend", "Backend / API", r"\.(?:py|js|ts|go|rs|java|kt|cs)$",
     r"\b(?:FastAPI|Flask)\s*\(|@(?:RestController|Controller)\b|\b(?:app|router)\.(?:get|post|put|delete|route)\s*\(|\bhttp\.(?:ListenAndServe|HandleFunc)\s*\(|\bMap(?:Get|Post|Controllers)\s*\("),
    ("cli", "Command-line tool", r"\.(?:py|rs|go|js|ts|cs|java)$",
     r"\b(?:argparse\.ArgumentParser|ArgumentParser|clap::Parser|Command::new|cobra\.Command|click\.command|commander\.program|System\.CommandLine)\b"),
    ("script", "Python application / script", r"\.py$", r"""if\s+__name__\s*==\s*['"]__main__['"]"""),
    ("executable", "Executable application", r"\.(?:go|rs|java)$",
     r"\bfunc\s+main\s*\(|\bfn\s+main\s*\(|\bpublic\s+static\s+void\s+main\s*\("),
    ("library", "Library / SDK", r"(?:^|/)(?:Cargo\.toml|CMakeLists\.txt)$",
     r"(?m)^\s*\[lib\]\s*$|\badd_library\s*\("),
    ("shell", "Shell / batch automation", r"\.(?:sh|bash|zsh|nu|bat|cmd)$", r"\S"),
    ("build", "Build automation", r"(?:^|/)(?:Makefile|Rakefile|CMakeLists\.txt|build\.gradle(?:\.kts)?)$", r"\S"),
    ("infra", "Infrastructure as code", r"\.(?:tf|bicep)$", r"\b(?:resource|provider|module)\b"),
    ("containers", "Container / orchestration configuration", r"(?:^|/)(?:Dockerfile(?:\.[^/]+)?|Containerfile)$", r"(?m)^\s*FROM\s+"),
    ("orchestration", "Container / orchestration configuration", r"\.ya?ml$",
     r"(?m)^\s*(?:services\s*:|kind\s*:\s*(?:Deployment|Pod|StatefulSet|DaemonSet|Job|CronJob)\b)"),
    ("notebook", "Notebook / data analysis", r"\.ipynb$", r'"cells"\s*:'),
    ("mobile", "Mobile app", r"\.(?:swift|kt|java|gradle|kts|xml)$",
     r"import\s+UIKit\b|com\.android\.application|android\.intent\.action\.MAIN"),
    ("macos-ui", "macOS app", r"\.swift$", r"import\s+AppKit\b"),
    ("native-ui", "Native desktop app", r"\.(?:c|cpp|rs|py)$",
     r"\b(?:CreateWindowEx[AW]?|gtk_application_new|tkinter\.Tk)\s*\("),
    ("embedded", "Embedded / firmware", r"\.(?:c|cpp|h|ino|cmake|txt)$",
     r"\bESP_PLATFORM\b|#\s*include\s*[<\"]Arduino\.h|zephyr_library\s*\("),
    ("contract", "Smart contract", r"\.(?:sol|rs)$",
     r"\bpragma\s+solidity\b|\bsoroban_sdk\b|\banchor_lang\b"),
]
COMPILED_TYPES = [(key, label, re.compile(path, re.I), re.compile(pattern))
                  for key, label, path, pattern in TYPE_RULES]


def application_findings(path, text):
    findings = []
    for key, label, path_pattern, pattern in COMPILED_TYPES:
        if path_pattern.search(path):
            match = pattern.search(text)
            if match:
                findings.append(evidence("application-" + key, label, path,
                                         text.count("\n", 0, match.start()) + 1))
    if PurePosixPath(path).name == "package.json":
        try:
            manifest = json.loads(text)
        except json.JSONDecodeError as error:
            logging.getLogger(__name__).warning("Application metadata not interpreted in %s: %s", path, error)
            return findings
        if not isinstance(manifest, dict):
            logging.getLogger(__name__).warning("Application metadata in %s is not an object", path)
            return findings
        dependencies = set()
        for field in ("dependencies", "devDependencies"):
            value = manifest.get(field, {})
            if isinstance(value, dict):
                dependencies.update(value)
            else:
                logging.getLogger(__name__).warning("Application metadata %s in %s is not an object", field, path)
        for packages, label in [
            ({"react-dom", "next", "@angular/core", "vue", "svelte", "astro"}, "Web frontend"),
            ({"express", "fastify", "@nestjs/core", "koa", "hono"}, "Backend / API"),
        ]:
            if packages & dependencies:
                findings.append(evidence("application-dependency", label, path))
        if manifest.get("bin"):
            findings.append(evidence("application-bin", "Command-line tool", path))
        if manifest.get("exports"):
            findings.append(evidence("application-package-exports", "Library / SDK", path))
    if PurePosixPath(path).name.lower() == "pyproject.toml":
        try:
            manifest = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            logging.getLogger(__name__).warning("Application metadata not interpreted in %s: %s", path, error)
            return findings
        project = manifest.get("project")
        if isinstance(project, dict) and project.get("scripts"):
            findings.append(evidence("application-python-scripts", "Command-line tool", path))
    return findings


def evidence(rule, label, path, line=1, confidence="medium", engine="project heuristic", **extra):
    return dict(rule=rule, label=label, path=path, line=line, confidence=confidence,
                engine=engine, **extra)


def metadata(path, text):
    """Read literal XML values only, rejecting DTDs/entities before parsing."""
    findings, notes = [], []
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        return [], ["DTD/entity declarations rejected"]
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return [], ["Malformed XML; metadata not interpreted"]
    positions = {}
    searchable = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S)
    if root.get("Sdk") == "Microsoft.NET.Sdk.Web":
        findings.append(evidence("metadata-web-sdk", "Backend / API", path))

    pending = [(root, False)]
    while pending:
        node, conditional = pending.pop()
        conditional = conditional or any(k.rsplit("}", 1)[-1].lower() == "condition" for k in node.attrib)
        name = node.tag.rsplit("}", 1)[-1]
        match = re.search(r"<(?:[\w.-]+:)?" + re.escape(name) + r"\b", searchable[positions.get(name, 0):])
        offset = positions.get(name, 0) + match.start() if match else 0
        positions[name] = offset + len(match[0]) if match else positions.get(name, 0)
        value = (node.text or "").strip()
        label = None
        if name in {"UseWPF", "UseWindowsForms", "UseMaui"} and value.lower() == "true":
            label = {"UseWPF": "WPF", "UseWindowsForms": "Windows Forms", "UseMaui": "Cross-platform: .NET MAUI"}[name]
        elif name == "OutputType" and value.lower() in {"exe", "winexe"}:
            label = "Executable"
        elif name == "ConfigurationType" and value == "Application":
            label = "Executable"
        elif (name == "OutputType" and value.lower() == "library"
              or name == "ConfigurationType" and value in {"DynamicLibrary", "StaticLibrary"}):
            label = "Library / SDK"
        elif name == "TargetFramework" or name == "TargetFrameworks":
            if re.search(r"\bnet[\d.]+-windows\b", value, re.I):
                label = "Windows target"
        elif name == "PackageReference":
            package = node.get("Include", "")
            label = {"Microsoft.WindowsAppSDK": "WinUI / Windows App SDK",
                     "Microsoft.NETCore.UniversalWindowsPlatform": "UWP",
                     "Avalonia": "Cross-platform: Avalonia",
                     "Avalonia.Desktop": "Cross-platform: Avalonia",
                     "Microsoft.Extensions.Hosting.WindowsServices": "Windows service integration",
                     "System.ServiceProcess.ServiceController": "Service management"}.get(package)
        elif name == "artifactId" and value.startswith("spring-boot-starter-web"):
            label = "Backend / API"
        elif name == "action" and node.get("{http://schemas.android.com/apk/res/android}name") == "android.intent.action.MAIN":
            label = "Mobile app"
        if label:
            findings.append(evidence("metadata-" + name, label, path,
                                     text.count("\n", 0, offset) + 1,
                                     "low" if conditional else "medium", "literal project metadata",
                                     conditional=conditional))
        pending.extend((child, conditional) for child in reversed(node))
    if root.tag.rsplit("}", 1)[-1].lower() == "service":
        values = {node.tag.rsplit("}", 1)[-1].lower(): (node.text or "").strip()
                  for node in root}
        if (re.fullmatch(r"(?:.*[/\\])?(?:pwsh|powershell)(?:\.exe)?", values.get("executable", ""), re.I)
                and re.search(r"(?:-File\b[^\n]*\.ps1|-Command\b)", values.get("arguments", ""), re.I)):
            match = re.search(r"<executable\b", searchable, re.I)
            findings.append(evidence("powershell-service-wrapper", "PowerShell-backed service", path,
                                     text.count("\n", 0, match.start()) + 1 if match else 1,
                                     "medium", "literal service-wrapper metadata",
                                     note="WinSW-style service host configuration; runtime not verified"))
    if any(item.get("conditional") for item in findings):
        notes.append("Conditional metadata is unevaluated supporting evidence")
    if any(node.tag.rsplit("}", 1)[-1] == "Import" for node in root.iter()):
        notes.append("MSBuild imports are not evaluated")
    return findings, notes


def powershell(path, text):
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in {".ps1", ".psm1", ".psd1"}:
        return []
    # Ignore standalone/ block comments; do not claim to fully parse PowerShell.
    cleaned = re.sub(r"<#.*?#>", lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S)
    cleaned = re.sub(r"(?m)^[ \t]*#.*$", "", cleaned)
    label = "PowerShell module" if suffix in {".psm1", ".psd1"} else "PowerShell script"
    found = [evidence("powershell-file", label, path, confidence="high")]
    if re.search(r"(?:^|/)(?:install|uninstall|setup)(?:[-_.][^/]*)?\.ps1$", path, re.I):
        found.append(evidence("powershell-installer", "PowerShell install script", path))
    management = re.search(r"\b(?:Get|New|Set|Start|Stop|Restart|Remove)-Service\b|\bsc(?:\.exe)?\s+(?:create|start|stop|delete)\b", cleaned, re.I)
    if management:
        found.append(evidence("powershell-management", "Service management", path,
                              cleaned.count("\n", 0, management.start()) + 1))
    # Creation of a service pointing to PowerShell is stronger than managing an
    # unrelated service, but does not prove SCM protocol/lifecycle correctness.
    registration = re.search(
        r"(?im)^[ \t]*(?:New-Service\b[^\n]*-BinaryPathName|sc(?:\.exe)?[ \t]+create\b[^\n]*binPath[ \t]*=)"
        r"[^\n]*\b(?:pwsh|powershell)(?:\.exe)?\b[^\n]*(?:-File\b[^\n]*\.ps1|-Command\b)", cleaned)
    if registration:
        found.append(evidence("powershell-service-command", "PowerShell service registration", path,
                              cleaned.count("\n", 0, registration.start()) + 1, "low",
                              note="Registered PowerShell command; service lifecycle not verified"))
    wrapper = re.search(r"(?im)^[ \t]*(?:&[ \t]+)?nssm(?:\.exe)?[ \t]+install[ \t]+\S+[ \t]+[\"']?(?:[^\n\"']*[/\\])?"
                        r"(?:pwsh|powershell)(?:\.exe)?[\"']?\s+[^\n]*(?:-File\b[^\n]*\.ps1|-Command\b)", cleaned)
    if wrapper:
        found.append(evidence("powershell-service-wrapper", "PowerShell-backed service", path,
                              cleaned.count("\n", 0, wrapper.start()) + 1, "medium",
                              note="NSSM service host command; runtime not verified"))
    return found


def classify_projects(files, classify, supplemental=()):
    files = sorted(files)
    manifests = [path for path, _ in files if PurePosixPath(path).suffix.lower() in PROJECT_SUFFIXES
                 or PurePosixPath(path).name.lower() in PROJECT_NAMES]
    projects = {path: {"path": path, "kind": ("PowerShell module" if path.lower().endswith(".psd1") else
                                           "MSBuild" if PurePosixPath(path).suffix.lower() in XML_SUFFIXES else
                                           PurePosixPath(path).name),
                       "files": [], "evidence": [], "notes": []} for path in manifests}
    directories = {}
    for manifest in manifests:
        directories.setdefault(PurePosixPath(manifest).parent, []).append(manifest)
    owners = {}
    for path, text in files:
        if path in projects:
            owner = path
        else:
            candidates = next((directories[parent] for parent in PurePosixPath(path).parents
                               if parent in directories), [])
            shared = PurePosixPath(path).suffix.lower() in {".props", ".targets"}
            owner = candidates[0] if len(candidates) == 1 and not shared else (
                "@shared" if shared else "@ambiguous" if candidates else "@unassigned")
        if owner not in projects:
            projects[owner] = {"path": ".", "kind": owner[1:], "files": [], "evidence": [],
                               "notes": ["No unique project ownership; evidence is not propagated to projects"]}
        owners[path] = owner
        project = projects[owner]
        project["files"].append(path)
        project["evidence"].extend(powershell(path, text))
        if PurePosixPath(path).suffix.lower() not in XML_SUFFIXES | {".xml"}:
            project["evidence"].extend(application_findings(path, text))
        if PurePosixPath(path).suffix.lower() in XML_SUFFIXES | {".xml"}:
            findings, notes = metadata(path, text)
            project["evidence"].extend(findings)
            project["notes"].extend(notes)
        else:
            for item in classify([(path, text)])["evidence"]:
                label = item["label"]
                if item["kind"] == "framework":
                    if label in {"Avalonia", "Electron", ".NET MAUI", "Flutter", "Qt", "React Native"}:
                        label = "Cross-platform: " + label
                    project["evidence"].append({**item, "label": label, "confidence": "medium"})
                elif item["label"] == "Windows services":
                    host = re.search(r"\b(?:UseWindowsService|AddWindowsService|StartServiceCtrlDispatcher[AW]?|RegisterServiceCtrlHandler[AW]?|ServiceBase\.Run)\s*\(", text)
                    project["evidence"].append({**item, "label": "Windows service" if host else "Service management",
                                               "confidence": "medium" if host else "low"})
    for item in supplemental:
        owner = owners.get(item.get("path"))
        if owner:
            # XML labels must come only from the safe literal parser; broad
            # engine regexes cannot evaluate conditions or distinguish comments.
            if PurePosixPath(item["path"]).suffix.lower() in XML_SUFFIXES | {".xml"}:
                continue
            label = item.get("label")
            if label == "Windows services":
                # Inspector's broad namespace rule also matches management code.
                label = "Service management"
            if label in {"Avalonia", "Electron", ".NET MAUI", "Flutter", "Qt", "React Native"}:
                label = "Cross-platform: " + label
            projects[owner]["evidence"].append({**item, "label": label,
                                               "confidence": item.get("confidence", "medium")})
    for project in projects.values():
        project["labels"] = sorted({item["label"] for item in project["evidence"]})
        project["confidence"] = max((item["confidence"] for item in project["evidence"]),
                                    key=RANK.get, default="low")
        project["notes"] = sorted(set(project["notes"]))
        project["label_confidence"] = {
            label: max((item["confidence"] for item in project["evidence"] if item["label"] == label), key=RANK.get)
            for label in project["labels"]}
    return list(projects.values())
