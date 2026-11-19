"""ACS-05: a completed critical/warning diagnostic must not be run twice.

Offline, no credentials, scheduled tasks, Git mutations, or phone access.
"""
import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "agents" / "supervisor.py"

def isolated_child_cycle():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Supervisor")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_run_child_cycle")
    module = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module)
    scope = {"Path": Path, "sys": sys, "subprocess": subprocess,
             "json": json, "time": __import__("time"), "Dict": Dict, "Any": Any,
             "__file__": str(SOURCE)}
    exec(compile(module, str(SOURCE), "exec"), scope)
    return scope["_run_child_cycle"]

def cycle_result(status, exitcode):
    return subprocess.CompletedProcess(
        args=["python", "run_acs_cycle.py", "ACS-05"], returncode=exitcode,
        stdout=json.dumps({"agent": "ACS-05", "status": status, "verified": True}) + "\n",
        stderr="",
    )

class CompletedFailureIsNotRetried(unittest.TestCase):
    def test_critical_is_not_rerun(self):
        with patch("subprocess.run", return_value=cycle_result("critical", 2)) as run, patch("time.sleep") as sleep:
            result = isolated_child_cycle()(object(), "ACS-05")
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "critical")
        self.assertEqual(result["attempt_count"], 1)

    def test_warning_is_not_rerun(self):
        with patch("subprocess.run", return_value=cycle_result("warning", 0)) as run, patch("time.sleep") as sleep:
            result = isolated_child_cycle()(object(), "ACS-05")
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "warning")

    def test_transient_execution_failure_still_gets_one_retry(self):
        with patch("subprocess.run", side_effect=[
            cycle_result("execution_failure", 3), cycle_result("healthy", 0)
        ]) as run, patch("time.sleep"):
            result = isolated_child_cycle()(object(), "ACS-05")
        self.assertEqual(run.call_count, 2)
        self.assertTrue(result["ok"])
        self.assertEqual(result["attempt_count"], 2)

if __name__ == "__main__":
    unittest.main()
