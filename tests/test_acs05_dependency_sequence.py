"""Regression tests for ACS-05 supervisor dependency sequencing.

Run: python3 -m unittest tests.test_acs05_dependency_sequence
No Gmail credentials, network, or runtime state required.
"""
import ast
import pathlib
import subprocess
import sys
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUPERVISOR_PATH = ROOT / "agents/supervisor.py"


def load_dependency_method():
    """Extract the method without importing unrelated supervisor dependencies."""
    module = ast.parse(SUPERVISOR_PATH.read_text(encoding="utf-8"))
    supervisor = next(node for node in module.body
                      if isinstance(node, ast.ClassDef) and node.name == "Supervisor")
    method = next(node for node in supervisor.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "_prepare_acs05_dependencies")
    isolated = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(isolated)
    namespace = {"Path": pathlib.Path, "subprocess": subprocess, "sys": sys}
    exec(compile(isolated, str(SUPERVISOR_PATH), "exec"), namespace)
    return namespace["_prepare_acs05_dependencies"]


class DependencyRecoveryTests(unittest.TestCase):
    def test_all_steps_run_in_required_order(self):
        method = load_dependency_method()
        with mock.patch("subprocess.run") as execute:
            execute.return_value.returncode = 0
            output = method(object())
        self.assertTrue(output["ok"])
        expected = ("tools/gmail_refresh_guard.py",
                    "tools/core_monitors_bundle.py",
                    "agents/prediction_feed_agent.py")
        paths = [str(item.args[0][1]) for item in execute.call_args_list]
        self.assertEqual(len(paths), 3)
        for actual, relative in zip(paths, expected):
            self.assertTrue(actual.endswith(relative), (actual, relative))
        self.assertTrue(all(step["ok"] for step in output["steps"].values()))

    def test_gmail_failure_is_not_masked_by_later_success(self):
        method = load_dependency_method()
        with mock.patch("subprocess.run") as execute:
            execute.side_effect = [
                subprocess.CompletedProcess([], 1, "", "secret"),
                subprocess.CompletedProcess([], 0, "", ""),
                subprocess.CompletedProcess([], 0, "", ""),
            ]
            output = method(object())
        self.assertFalse(output["ok"])
        self.assertEqual(execute.call_count, 3)
        self.assertFalse(output["steps"]["gmail_oauth"]["ok"])
        self.assertTrue(output["steps"]["prediction_feed"]["ok"])
        self.assertNotIn("secret", str(output))

    def test_exception_still_runs_following_steps(self):
        method = load_dependency_method()
        with mock.patch("subprocess.run") as execute:
            execute.side_effect = [
                TimeoutError("private path"),
                subprocess.CompletedProcess([], 0, "", ""),
                subprocess.CompletedProcess([], 0, "", ""),
            ]
            output = method(object())
        self.assertFalse(output["ok"])
        self.assertEqual(output["steps"]["gmail_oauth"]["error_type"], "TimeoutError")
        self.assertEqual(execute.call_count, 3)
        self.assertNotIn("private path", str(output))

    def test_child_cycle_order_and_degraded_dependency_gate(self):
        src = SUPERVISOR_PATH.read_text(encoding="utf-8")
        module = ast.parse(src)
        supervisor = next(node for node in module.body
                          if isinstance(node, ast.ClassDef) and node.name == "Supervisor")
        run = next(node for node in supervisor.body
                   if isinstance(node, ast.FunctionDef) and node.name == "run")
        text = ast.get_source_segment(src, run)
        self.assertIn('if agent == "ACS-05":', text)
        self.assertIn('results["acs_05_dependencies"] = self._prepare_acs05_dependencies()', text)
        self.assertIn('"acs_05_dependencies", "encrypted_backup"', text)


if __name__ == "__main__":
    unittest.main()
