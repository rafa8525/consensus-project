"""ACS-04 notification command status tests (no real notifications)."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agents.infrastructure_guardian import Config, InfrastructureGuardian


class NotificationSafetyTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        repo = root / "repo"
        memory = root / "memory"
        repo.mkdir()
        memory.mkdir()
        self.guardian = InfrastructureGuardian(
            Config(
                repo_root=repo, memory_root=memory,
                state_dir=root / "state",
                quota_bytes=10_000_000,
                notification_command="fake-notifier",
            ),
            apply_repairs=False,
        )
        self.bad = {"overall_status": "warning", "findings": [
            {"severity": "warning", "message": "test problem"}
        ]}

    def test_nonzero_exit_is_reported(self):
        with patch("agents.infrastructure_guardian.subprocess.run",
                   return_value=SimpleNamespace(returncode=6)):
            result = self.guardian.notify(self.bad)
        self.assertEqual(result, {"status": "command_failed", "returncode": 6})

    def test_zero_exit_does_not_claim_delivery(self):
        with patch("agents.infrastructure_guardian.subprocess.run",
                   return_value=SimpleNamespace(returncode=0)):
            result = self.guardian.notify(self.bad)
        self.assertEqual(result["status"], "command_succeeded")
        self.assertNotIn("delivered", result)

    def test_exception_is_reported_without_secrets(self):
        with patch("agents.infrastructure_guardian.subprocess.run",
                   side_effect=RuntimeError("hidden-secrets")):
            result = self.guardian.notify(self.bad)
        self.assertEqual(result, {"status": "command_failed", "error_type": "RuntimeError"})
        self.assertNotIn("hidden-secrets", json.dumps(result))

    def test_status_report_contains_failed_notification(self):
        with patch.object(self.guardian, "acquire_lock"), \
             patch.object(self.guardian, "release_lock"), \
             patch.object(self.guardian, "check_disk"), \
             patch.object(self.guardian, "check_logs"), \
             patch.object(self.guardian, "check_repository"), \
             patch.object(self.guardian, "notify",
                          return_value={"status": "command_failed", "returncode": 6}):
            self.guardian.add("warning", "TEST", "notification test")
            rc = self.guardian.execute()
        data = json.loads(self.guardian.status_path.read_text())
        self.assertEqual(rc, 1)
        self.assertEqual(data["notification"]["status"], "command_failed")
        self.assertEqual(data["notification"]["returncode"], 6)


if __name__ == "__main__":
    unittest.main()
