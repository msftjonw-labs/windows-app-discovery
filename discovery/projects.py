"""Conservative project attribution; confidence describes evidence, not probability.

MSBuild conditions/imports/globs are never evaluated. Shared and ambiguous sources
remain explicit inventory entries instead of being attributed to every project.
"""

from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET

PROJECT_SUFFIXES = {".csproj", ".vbproj", ".fsproj", ".vcxproj", ".psd1"}
PROJECT_NAMES = {"package.json", "pyproject.toml", "cargo.toml", "go.mod",
                 "cmakelists.txt", "pom.xml", "pubspec.yaml", "build.gradle", "build.gradle.kts"}
XML_SUFFIXES = {".csproj", ".vbproj", ".fsproj", ".vcxproj", ".props", ".targets"}
DESKTOP = {"Windows Forms", "WPF", "WinUI / Windows App SDK", "UWP"}
RANK = {"low": 0, "medium": 1, "high": 2}


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
