import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repair_report_master", ROOT / "tools/report_master.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
class ReportMasterFailClosedTests(unittest.TestCase):
    def test_required_child_nonzero_causes_failure(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(MODULE.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)):
            self.assertFalse(MODULE.run("generate_weekly_report.py"))
    def test_required_child_success(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(MODULE.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
            self.assertTrue(MODULE.run("generate_weekly_report.py"))
    def test_missing_child_fails(self):
        with patch.object(Path, "is_file", return_value=False):
            self.assertFalse(MODULE.run("missing.py"))
    def test_main_fails_if_any_child_fails(self):
        with patch.object(MODULE, "run", side_effect=[True, False]):
            self.assertEqual(MODULE.main(), 1)
    def test_main_passes_only_if_both_pass(self):
        with patch.object(MODULE, "run", side_effect=[True, True]):
            self.assertEqual(MODULE.main(), 0)
if __name__ == "__main__":
    unittest.main()
