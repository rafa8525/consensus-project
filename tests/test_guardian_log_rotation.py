"""Regression tests for ACS-04 log rotation (isolated temporary files only)."""
import tempfile
import unittest
from pathlib import Path

from agents.infrastructure_guardian import Config, InfrastructureGuardian


class LogRotationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.memory = self.root / "memory"
        self.logs = self.memory / "logs"
        self.logs.mkdir(parents=True)
        self.repo.mkdir()
        self.guardian = InfrastructureGuardian(
            Config(
                repo_root=self.repo,
                memory_root=self.memory,
                state_dir=self.root / "state",
                quota_bytes=10_000_000,
                log_rotate_bytes=16,
                max_rotated_logs=2,
            ),
            apply_repairs=True,
        )

    def test_active_logs_rotate_but_status_and_old_rotations_do_not(self):
        live = self.logs / "worker.log"
        live.write_text("A" * 32)
        status = self.logs / "health.json"
        status.write_text("S" * 32)
        old = self.logs / "worker.log.2"
        old.write_text("old_backup")

        self.guardian.check_logs()

        self.assertEqual(live.read_text(), "")
        self.assertEqual((self.logs / "worker.log.1").read_text(), "A" * 32)
        self.assertEqual(status.read_text(), "S" * 32)
        self.assertFalse((self.logs / "health.json.1").exists())
        self.assertEqual(old.read_text(), "old_backup")

        # Running again without new log growth must not consume a backup.
        self.guardian.check_logs()
        self.assertEqual((self.logs / "worker.log.1").read_text(), "A" * 32)
        self.assertEqual(old.read_text(), "old_backup")

    def test_jsonl_rotates_and_archives_are_skipped(self):
        events = self.logs / "events.jsonl"
        events.write_text("E" * 32)
        archive = self.logs / "archive"
        archive.mkdir()
        historical = archive / "old.log"
        historical.write_text("H" * 32)

        self.guardian.check_logs()

        self.assertEqual((self.logs / "events.jsonl.1").read_text(), "E" * 32)
        self.assertEqual(historical.read_text(), "H" * 32)

    def test_symlink_to_external_log_is_not_rotated(self):
        outside = self.root / "outside.log"
        outside.write_text("X" * 32)
        link = self.logs / "external.log"
        link.symlink_to(outside)
        self.guardian.check_logs()
        self.assertEqual(outside.read_text(), "X" * 32)
        self.assertTrue(link.is_symlink())


if __name__ == "__main__":
    unittest.main()
