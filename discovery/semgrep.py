"""Opt-in local Semgrep hints, isolated from repository configuration."""

import hashlib
import json
import os
from pathlib import Path
import subprocess

VERSION = "local-hints-2"
RULES = [
    {"id": "pilot-windows-service", "languages": ["generic"], "severity": "INFO",
     "message": "Windows service host integration",
     "pattern-regex": r"\b(?:UseWindowsService|AddWindowsService)\s*\("},
    {"id": "pilot-powershell-host", "languages": ["generic"], "severity": "INFO",
     "message": "Embedded PowerShell host (not proof of a service)",
     "pattern-regex": r"\bSystem\.Management\.Automation\b"},
    {"id": "pilot-csharp-winforms", "languages": ["csharp"], "severity": "INFO",
     "message": "C# class structurally inherits Windows Forms Form",
     "pattern-either": [
         {"pattern": "class $FORM : System.Windows.Forms.Form { ... }"},
         {"patterns": [
             {"pattern-inside": "using System.Windows.Forms;\n..."},
             {"pattern": "class $FORM : Form { ... }"},
         ]},
     ]},
    {"id": "pilot-csharp-service-host", "languages": ["csharp"], "severity": "INFO",
     "message": "C# syntax invokes Windows service host integration",
     "pattern-either": [
         {"pattern": "$HOST.UseWindowsService(...)"},
         {"pattern": "$SERVICES.AddWindowsService(...)"},
     ]},
    {"id": "pilot-csharp-powershell-host", "languages": ["csharp"], "severity": "INFO",
     "message": "C# syntax creates an embedded PowerShell host (not proof of a service)",
     "pattern-either": [
         {"pattern": "System.Management.Automation.PowerShell.Create(...)"},
         {"patterns": [
             {"pattern-inside": "using System.Management.Automation;\n..."},
             {"pattern": "PowerShell.Create(...)"},
         ]},
     ]},
]
LABELS = {"pilot-windows-service": "Windows service",
          "pilot-powershell-host": "PowerShell host",
          "pilot-csharp-winforms": "Windows Forms",
          "pilot-csharp-service-host": "Windows service",
          "pilot-csharp-powershell-host": "PowerShell host"}
STRUCTURAL_RULES = {"pilot-csharp-winforms", "pilot-csharp-service-host", "pilot-csharp-powershell-host"}


def environment(work):
    return {**os.environ, "SEMGREP_SEND_METRICS": "off", "SEMGREP_ENABLE_VERSION_CHECK": "0",
            "SEMGREP_SETTINGS_FILE": str(work / "semgrep-settings.yml"),
            "SEMGREP_APP_TOKEN": "", "NO_PROXY": "*", "HTTP_PROXY": "", "HTTPS_PROXY": ""}


def identity(executable, work=None):
    rules = {"rules": VERSION, "rules_digest": hashlib.sha256(
        json.dumps(RULES, sort_keys=True).encode()).hexdigest()}
    if executable is None:
        return {"status": "disabled", **rules}
    executable = Path(executable).resolve()
    try:
        # Hash the local launcher as well as recording the configured engine. No
        # stale reuse even when a launcher is replaced at the same path.
        digest = hashlib.sha256(executable.read_bytes()).hexdigest()
        work = Path(work or executable.parent).resolve()
        probe = subprocess.run([str(executable), "--version"], cwd=work,
                               env=environment(work), capture_output=True, text=True, timeout=15)
        if probe.returncode:
            raise OSError("Semgrep version probe failed")
        return {"status": "configured", "executable": str(executable),
                "digest": digest, "version": probe.stdout.strip()[:100], **rules}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "unavailable", "executable": str(executable),
                "reason": str(error), **rules}


def scan(source, executable, work, files):
    if executable is None:
        return {"status": "disabled", "evidence": []}
    config = work / "semgrep-rules.json"
    config.write_text(json.dumps({"rules": RULES}), encoding="utf-8")
    try:
        version = subprocess.run([str(Path(executable).resolve()), "--version"], cwd=work,
                                 env=environment(work), capture_output=True, text=True, timeout=15)
        if version.returncode:
            return {"status": "unavailable", "reason": "Version probe failed", "evidence": []}
        result = subprocess.run(
            [str(Path(executable).resolve()), "scan", "--config", str(config.resolve()),
             "--json", "--metrics=off", "--disable-version-check", "--no-git-ignore",
             "--no-rewrite-rule-ids", "--oss-only", "--timeout", "10", "--max-target-bytes", "8388608",
             str(source.resolve())], cwd=work, env=environment(work),
            capture_output=True, text=True, timeout=90)
        if result.returncode:
            return {"status": "partial", "reason": f"Semgrep exit {result.returncode}", "evidence": []}
        report = json.loads(result.stdout)
        findings, rejected = [], 0
        allowed = {path: text.count("\n") + 1 for path, text in files}
        for match in report["results"]:
            raw = Path(match["path"])
            try:
                if ".." in raw.parts or ("\\" in str(raw) and os.name != "nt"):
                    raise ValueError("Unsafe source path")
                path = (raw if raw.is_absolute() else work / raw).resolve().relative_to(source.resolve()).as_posix()
                line = match["start"]["line"]
                if (path not in allowed or type(line) is not int or line < 1
                        or line > allowed[path]):
                    raise ValueError("Invalid source location")
                label = LABELS[match["check_id"]]
            except (ValueError, KeyError, TypeError):
                rejected += 1
                continue
            findings.append({"rule": match["check_id"], "label": label, "path": path,
                             "line": line, "confidence": "high" if match["check_id"] in STRUCTURAL_RULES else "medium",
                             "engine": ("Semgrep (structural C# local rule)" if match["check_id"] in STRUCTURAL_RULES
                                        else "Semgrep (supplemental text rule)")})
        return {"status": "partial" if report.get("errors") or rejected else "success",
                "version": version.stdout.strip()[:100], "evidence": findings,
                "errors": len(report.get("errors", [])), "rejected_findings": rejected}
    except subprocess.TimeoutExpired:
        return {"status": "partial", "reason": "Semgrep timeout", "evidence": []}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {"status": "unavailable", "reason": str(error)[:300], "evidence": []}
