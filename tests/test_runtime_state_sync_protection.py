"""Regression: runtime state is preserved, not treated as an unsafe source edit."""
from __future__ import annotations
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("acs_safe_sync_runtime_test", ROOT / "agents/safe_sync_live_branch.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class RuntimeSyncProtectionTests(unittest.TestCase):
    def test_runtime_state_classified_as_runtime(self):
        statuses = (
            " M memory/state/task_failure_guardian_state.json\n"
            " M memory/agents/state.json\n"
            " M memory/security_audit_schedule.txt\n"
            " M memory/logs/system/heartbeat.md\n"
        )
        fake = subprocess.CompletedProcess(["git", "status"], 0, statuses, "")
        with patch.object(mod, "run", return_value=fake):
            runtime, source = mod.classify_changes()
        self.assertEqual(source, [])
        self.assertEqual(len(runtime), 4)
        self.assertIn("memory/state/task_failure_guardian_state.json", runtime)

    def test_actual_source_change_remains_blocked(self):
        fake = subprocess.CompletedProcess(["git"], 0,
            " M memory/state/task_failure_guardian_state.json\n"
            " M agents/supervisor.py\n", "")
        with patch.object(mod, "run", return_value=fake):
            runtime, source = mod.classify_changes()
        self.assertEqual(runtime, ["memory/state/task_failure_guardian_state.json"])
        self.assertEqual(source, ["agents/supervisor.py"])

    def test_safety_no_forced_git_reset(self):
        body = (ROOT / "agents/safe_sync_live_branch.py").read_text()
        self.assertNotIn('"reset", "--hard"', body)
        self.assertNotIn('"push", "--force"', body)
        self.assertIn("restore_runtime_from_stash", body)

if __name__ == "__main__":
    unittest.main()
