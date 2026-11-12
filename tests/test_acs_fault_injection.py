"""Isolated failure-injection tests. No network, SMS, live agents or credentials."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, Mock
from agents import run_acs_cycle as cycle


class FailureInjection(unittest.TestCase):
    def fake_process(self, component, rc, stdout=""):
        fake = Mock(returncode=rc, stdout=stdout, stderr="")
        with patch.object(cycle.subprocess, "run", return_value=fake):
            return cycle.run_process(component, Path("/never/execute.py"))

    def test_acs02_valid_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker.json"
            marker.write_text(json.dumps({"status":"ok", "last_success_utc":datetime.now(timezone.utc).isoformat()}))
            with patch.object(cycle, "ABSORB_MARKER", marker):
                self.assertEqual(cycle.verify_absorption_marker()["status"], "healthy")

    def test_acs02_bad_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker.json"
            for data, expected in [
                ("{corrupt", "critical"),
                (json.dumps({"status":"failed"}), "critical"),
                (json.dumps({"status":"ok", "last_success_utc":(datetime.now(timezone.utc)-timedelta(hours=37)).isoformat()}), "warning"),
                (json.dumps({"status":"ok", "last_success_utc":(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat()}), "critical"),
            ]:
                marker.write_text(data)
                with patch.object(cycle, "ABSORB_MARKER", marker):
                    self.assertEqual(cycle.verify_absorption_marker()["status"], expected)

    def test_acs02_worker_failure_does_not_write_success_marker(self):
        with patch.object(cycle, "run_process", return_value={"component":"absorb_memory", "status":"execution_failure"}) as runner:
            result = cycle.run_acs02()
        self.assertEqual(result[1]["status"], "execution_failure")
        self.assertTrue(result[1]["skipped"])
        self.assertEqual(runner.call_count, 1)

    def test_acs02_marker_writer_failure(self):
        with patch.object(cycle, "run_process", side_effect=[
            {"component":"absorb_memory","status":"healthy"},
            {"component":"public_marker","status":"execution_failure"}]):
            result = cycle.run_acs02()
        self.assertEqual(cycle.overall_status(result), "execution_failure")
        self.assertEqual(len(result), 2)

    def test_acs03_component_crash_detected(self):
        self.assertEqual(self.fake_process("health_master", 1)["status"], "execution_failure")
        self.assertEqual(cycle.overall_status([{"status":"healthy"},{"status":"execution_failure"}]), "execution_failure")

    def test_acs04_guardian_exit_codes(self):
        for rc, expected in [(0,"healthy"),(1,"warning"),(2,"critical"),(3,"execution_failure"),(9,"execution_failure")]:
            with self.subTest(rc=rc):
                self.assertEqual(self.fake_process("infrastructure_guardian", rc)["status"], expected)

    def test_acs05_continuity_markers(self):
        cases = [
            (0,"END status=OK","healthy"),
            (0,"END status=WARN critical=0 warning=2","warning"),
            (2,"END status=CRITICAL critical=1","critical"),
            (0,"END status=CRITICAL","execution_failure"),
            (2,"END status=OK","execution_failure"),
            (2,"END status=WARN","execution_failure"),
            (0,"END status=OKAY","execution_failure"),
            (0,"", "execution_failure"),
            (0,"END status=OK\\nEND status=OK","execution_failure"),
            (3,"END status=OK","execution_failure"),
        ]
        for rc, stdout, expected in cases:
            with self.subTest(rc=rc, stdout=stdout):
                self.assertEqual(self.fake_process("continuity_guardian",rc,stdout)["status"], expected)

    def test_process_timeout(self):
        with patch.object(cycle.subprocess, "run", side_effect=TimeoutError("simulated")):
            result = cycle.run_process("fitness_tracking_verifier",Path("/never/execute.py"))
        self.assertEqual(result["status"],"execution_failure")

    def test_state_write_atomic_and_accurate(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(cycle, "STATE", Path(tmp)):
                state = cycle.write_state("ACS-04", cycle.now(), [{"status":"critical"}])
                saved = json.loads((Path(tmp)/"acs04_state.json").read_text())
                self.assertEqual(saved["status"],"critical")
                self.assertEqual(state["status"], saved["status"])
                self.assertFalse(list(Path(tmp).glob("*.tmp")))

    def test_unknown_status_fails_closed(self):
        self.assertEqual(cycle.overall_status([{"status":"not-real"}]),"execution_failure")
        self.assertEqual(cycle.overall_status([]),"execution_failure")


if __name__ == "__main__":
    unittest.main()
