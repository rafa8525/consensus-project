"""Regression tests for the ACS-05 child exit/terminal-marker contract.

Run: python -m unittest -v tests.test_acs05_status_protocol
No production agent or OAuth credentials are needed.
"""
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from agents import run_acs_cycle as cycle


class ACS05StatusProtocolTests(unittest.TestCase):
    def run_case(self, code, stdout):
        fake = subprocess.CompletedProcess(["python", "guardian"], code, stdout, "")
        with patch.object(cycle.subprocess, "run", return_value=fake):
            return cycle.run_process("continuity_guardian", Path("/fake/guardian.py"))

    def test_critical_is_classified_as_critical(self):
        result = self.run_case(2, "START\nCRITICAL foo\nEND status=CRITICAL critical=1 warning=0\n")
        self.assertEqual(result["status"], "critical")
        self.assertIsNone(result["classification_reason"])

    def test_ok(self):
        self.assertEqual(self.run_case(0, "END status=OK\n")["status"], "healthy")

    def test_warning(self):
        self.assertEqual(self.run_case(0, "END status=WARN critical=0 warning=1\n")["status"], "warning")

    def test_unexpected_exit_is_execution_failure_with_reason(self):
        result = self.run_case(3, "END status=CRITICAL critical=1 warning=0\n")
        self.assertEqual(result["status"], "execution_failure")
        self.assertEqual(result["classification_reason"], "unexpected_child_exit_code")

    def test_conflicting_exit_is_execution_failure_with_reason(self):
        result = self.run_case(0, "END status=CRITICAL\n")
        self.assertEqual(result["status"], "execution_failure")
        self.assertEqual(result["classification_reason"], "exit_code_marker_disagreement")

    def test_duplicate_markers_fail_closed(self):
        result = self.run_case(2, "END status=CRITICAL\nEND status=CRITICAL\n")
        self.assertEqual(result["status"], "execution_failure")
        self.assertEqual(result["classification_reason"], "missing_or_duplicate_terminal_marker")

    def test_truncated_stdout_does_not_lose_marker_for_classification(self):
        result = self.run_case(2, "x" * 5000 + "\nEND status=CRITICAL\n")
        self.assertEqual(result["status"], "critical")
        self.assertLessEqual(len(result["stdout"]), 4000)

    def test_missing_marker_fails_closed(self):
        result = self.run_case(2, "START\nCRITICAL foo\n")
        self.assertEqual(result["status"], "execution_failure")
        self.assertEqual(result["classification_reason"], "missing_or_duplicate_terminal_marker")


if __name__ == "__main__":
    unittest.main()
