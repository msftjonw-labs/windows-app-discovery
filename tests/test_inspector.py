"""Real-tool contract tests; set INSPECTOR_PATH to enable."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from discovery.pilot import inspect_sources


@unittest.skipUnless(os.environ.get("INSPECTOR_PATH"), "Set INSPECTOR_PATH to run real Inspector tests")
class InspectorIntegrationTests(unittest.TestCase):
    def inspect(self, files):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = work / "source"
            source.mkdir()
            for name, text in files.items():
                (source / name).write_text(text, encoding="utf-8")
            return inspect_sources(source, Path(os.environ["INSPECTOR_PATH"]), work)

    def test_real_windows_components_and_framework(self):
        result = self.inspect({
            "Program.cs": 'using System.Windows.Forms;\n[DllImport("user32.dll")] static extern void Test();\n[ComImport] class Component {}',
            "native.cpp": '#include <windows.h>\nvoid test() { CoInitializeEx(0, 0); D3D11CreateDevice(); }',
            "App.csproj": "<Project><UseWPF>true</UseWPF></Project>",
        })
        self.assertEqual(set(result["components"]), {"Win32", "COM", ".NET native interop", "DirectX"})
        self.assertIn("Windows Forms", result["frameworks"])
        self.assertIn("WPF", result["frameworks"])
        self.assertTrue(all(e["line"] >= 1 for e in result["evidence"]))
        self.assertTrue(all(not Path(e["path"]).is_absolute() for e in result["evidence"]))

    def test_no_matches_is_valid_empty_output(self):
        result = self.inspect({"Library.cs": "public class Library { public int Value = 1; }"})
        self.assertEqual(result["components"], [])
        self.assertEqual(result["frameworks"], [])
        self.assertEqual(result["incomplete"], {})

    @patch("discovery.pilot.MAX_INSPECTOR_FILES", 1)
    def test_real_batches_preserve_all_component_findings(self):
        result = self.inspect({
            "one.cpp": "#include <windows.h>\n",
            "two.cpp": "void test() { CoInitializeEx(0, 0); }\n",
        })
        self.assertEqual(set(result["components"]), {"Win32", "COM"})
        self.assertEqual({e["path"] for e in result["evidence"]}, {"one.cpp", "two.cpp"})
        self.assertEqual(result["incomplete"], {})

    def test_non_ascii_binary_heuristic_is_not_reported_as_complete(self):
        with self.assertLogs("pilot", level="WARNING"):
            result = self.inspect({"Library.cs": "// " + "\u3042" * 300 + "\npublic class Library {}"})
        self.assertEqual(result["incomplete"]["filesSkipped"], 1)


if __name__ == "__main__":
    unittest.main()
