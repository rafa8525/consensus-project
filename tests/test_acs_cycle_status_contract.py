"""Isolated subprocess-result tests for ACS-02..ACS-05 status handling."""
import tempfile
import json
from datetime import datetime, timedelta, timezone
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agents import run_acs_cycle as harness


class CycleStatusTests(unittest.TestCase):
    def check_continuity(self, exit_code, marker, expected):
        out = f"START continuity_guardian\\nEND status={marker}\\n" if marker else "START continuity_guardian\\n"
        proc = SimpleNamespace(returncode=exit_code, stdout=out, stderr="")
        with patch.object(harness.subprocess, "run", return_value=proc):
            status = harness.run_process("continuity_guardian", Path("/mock/guardian.py"))
        self.assertEqual(status["status"], expected)
        self.assertEqual(status["ok"], expected == "healthy")

    def test_success_marker_with_success_exit(self):
        self.check_continuity(0, "OK", "healthy")

    def test_warning_marker_with_success_exit(self):
        self.check_continuity(0, "WARN", "warning")

    def test_critical_marker_with_documented_exit(self):
        self.check_continuity(2, "CRITICAL", "critical")

    def test_ok_marker_with_failure_exit_fails_closed(self):
        self.check_continuity(1, "OK", "execution_failure")

    def test_ok_marker_with_critical_exit_fails_closed(self):
        self.check_continuity(2, "OK", "execution_failure")

    def test_critical_marker_with_zero_exit_fails_closed(self):
        self.check_continuity(0, "CRITICAL", "execution_failure")

    def test_missing_marker_fails_closed(self):
        self.check_continuity(0, None, "execution_failure")

    def test_infrastructure_guardian_exit_codes(self):
        for code, expected in [(0, "healthy"), (1, "warning"), (2, "critical"), (3, "execution_failure")]:
            with self.subTest(code=code):
                proc = SimpleNamespace(returncode=code, stdout="", stderr="")
                with patch.object(harness.subprocess, "run", return_value=proc):
                    result = harness.run_process("infrastructure_guardian", Path("/mock/infra.py"))
                self.assertEqual(result["status"], expected)

    def test_absorption_worker_failure_skips_marker(self):
        with patch.object(harness, "run_process", return_value={"status": "execution_failure", "ok": False}) as run:
            results = harness.run_acs02()
        self.assertEqual(results[-1]["status"], "execution_failure")
        self.assertTrue(results[-1]["skipped"])
        run.assert_called_once()

    def test_overall_status_prefers_worst_failure(self):
        statuses = [{"status": s} for s in ("healthy", "warning", "critical", "execution_failure")]
        self.assertEqual(harness.overall_status(statuses), "execution_failure")

    def test_empty_results_fail_closed(self):
        self.assertEqual(harness.overall_status([]), "execution_failure")

    def test_future_absorption_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / "marker.json"
            future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            marker.write_text(json.dumps({"status": "ok", "last_success_utc": future}))
            with patch.object(harness, "ABSORB_MARKER", marker):
                result = harness.verify_absorption_marker()
        self.assertEqual(result["status"], "critical")
        self.assertFalse(result["ok"])

    def test_current_absorption_marker_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / "marker.json"
            current = datetime.now(timezone.utc).isoformat()
            marker.write_text(json.dumps({"status": "ok", "last_success_utc": current}))
            with patch.object(harness, "ABSORB_MARKER", marker):
                result = harness.verify_absorption_marker()
        self.assertEqual(result["status"], "healthy")
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
