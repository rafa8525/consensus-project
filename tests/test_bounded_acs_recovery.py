"""No live calls: regression tests for bounded ACS recovery."""
import json
import unittest
from unittest.mock import patch
from agents import run_acs_cycle
from agents.supervisor import Supervisor


class RecoveryTests(unittest.TestCase):
    def test_marker_writer_recovers_without_repeating_absorption(self):
        calls = []
        responses = [
            {"status": "healthy", "ok": True},
            {"status": "execution_failure", "ok": False},
            {"status": "healthy", "ok": True},
        ]
        def fake_run(*args):
            calls.append(args[0])
            return responses.pop(0).copy()
        with patch.object(run_acs_cycle, "run_process", side_effect=fake_run), patch.object(
            run_acs_cycle, "verify_absorption_marker",
            return_value={"status": "healthy", "ok": True}
        ):
            results = run_acs_cycle.run_acs02()
        self.assertEqual(calls, ["absorb_memory", "write_absorption_public_marker",
                                 "write_absorption_public_marker"])
        self.assertEqual(run_acs_cycle.overall_status(results), "healthy")
        self.assertTrue(results[1]["recovered"])

    def test_marker_writer_fails_closed_after_one_retry(self):
        calls = []
        def fake_run(component, *args):
            calls.append(component)
            return {"status": "healthy" if component == "absorb_memory"
                    else "execution_failure", "ok": component == "absorb_memory"}
        with patch.object(run_acs_cycle, "run_process", side_effect=fake_run):
            result = run_acs_cycle.run_acs02()
        self.assertEqual(calls.count("absorb_memory"), 1)
        self.assertEqual(calls.count("write_absorption_public_marker"), 2)
        self.assertEqual(run_acs_cycle.overall_status(result), "execution_failure")

    def test_supervisor_does_not_retry_warning(self):
        self._check_child("ACS-05", "warning", 1)

    def test_supervisor_does_not_retry_critical(self):
        self._check_child("ACS-04", "critical", 2)

    def test_supervisor_retries_infra_execution_error(self):
        self._check_child("ACS-04", "execution_failure", 3, expected_attempts=2)

    def _check_child(self, agent, status, rc, expected_attempts=1):
        calls = []
        class Proc:
            returncode = rc
            stdout = json.dumps({"agent": agent, "status": status})
            stderr = ""
        def fake_subprocess(*args, **kwargs):
            calls.append(True)
            return Proc()
        with patch("agents.supervisor.subprocess.run", side_effect=fake_subprocess), patch(
            "agents.supervisor.time.sleep"
        ):
            result = Supervisor({})._run_child_cycle(agent)
        self.assertEqual(len(calls), expected_attempts)
        self.assertEqual(result["attempt_count"], expected_attempts)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
