"""Regression tests: ACS-01 must not report success for a degraded cycle.

Uses mocks only: no agent, Git, network, or PythonAnywhere process is run.
"""
import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents import supervisor


class SupervisorExitStatusTests(unittest.TestCase):
    def assert_main_exit(self, supervisor_result, bridge_returncode, expected):
        bridge_process = SimpleNamespace(
            returncode=bridge_returncode,
            stdout="",
            stderr="",
        )
        with patch.object(supervisor.Supervisor, "safe_run", return_value=supervisor_result), \
             patch.object(supervisor.subprocess, "run", return_value=bridge_process), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(supervisor.main(), expected)

    def test_healthy_supervisor_and_bridge_return_success(self):
        self.assert_main_exit(
            {"ok": True, "result": {"status": "ok", "results": {"system_health": {"ok": True}}}}, 0, 0
        )

    def test_degraded_supervisor_and_healthy_bridge_return_failure(self):
        self.assert_main_exit(
            {"ok": True, "result": {"status": "degraded"}}, 0, 1
        )

    def test_safe_run_exception_return_failure(self):
        self.assert_main_exit(
            {"ok": False, "error_type": "RuntimeError"}, 0, 1
        )

    def test_missing_cycle_status_returns_failure(self):
        self.assert_main_exit({"ok": True, "result": {}}, 0, 1)

    def test_healthy_supervisor_and_failed_bridge_return_failure(self):
        # The bridge is retried once; both attempts fail in this mocked test.
        self.assert_main_exit(
            {"ok": True, "result": {"status": "ok", "results": {"system_health": {"ok": True}}}}, 1, 1
        )


if __name__ == "__main__":
    unittest.main()
