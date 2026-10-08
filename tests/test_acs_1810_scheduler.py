import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from tools import run_1810_with_backup as wrapper


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.receipt = Path(self.tmp.name) / "receipt.json"
        self.now = datetime(2026, 10, 8, 22, 0, tzinfo=timezone.utc)

    def save(self, **changes):
        r = {
            "status": "uploaded_verified", "restore_verified": True, "file_count": 32,
            "remote_id": "fake-remote-id", "encrypted_sha256": "a" * 64,
            "finished_at_utc": (self.now - timedelta(hours=1)).isoformat()
        }
        r.update(changes)
        self.receipt.write_text(json.dumps(r))

    def test_verified_today_skips_duplicate(self):
        self.save()
        self.assertTrue(wrapper.already_verified_today(self.receipt, self.now))

    def test_missing_receipt_needs_backup(self):
        self.assertFalse(wrapper.already_verified_today(self.receipt, self.now))

    def test_prior_day_needs_backup(self):
        self.save(finished_at_utc=(self.now - timedelta(days=1)).isoformat())
        self.assertFalse(wrapper.already_verified_today(self.receipt, self.now))

    def test_invalid_receipt_needs_backup(self):
        self.save(restore_verified=False)
        self.assertFalse(wrapper.already_verified_today(self.receipt, self.now))

    def test_future_receipt_needs_backup(self):
        self.save(finished_at_utc=(self.now + timedelta(hours=3)).isoformat())
        self.assertFalse(wrapper.already_verified_today(self.receipt, self.now))

    def test_failure_does_not_block_subsequent_steps(self):
        with patch.object(wrapper, "PRIVATE", Path(self.tmp.name)), \
             patch.object(wrapper, "LOCK", Path(self.tmp.name) / "scheduler.lock"), \
             patch.object(wrapper, "SUCCESS", self.receipt), \
             patch.object(wrapper, "run_step", side_effect=[False, True, True, True]) as run:
            self.save()
            self.assertEqual(wrapper.run_all(), 1)
            self.assertEqual(run.call_count, 3)

    def test_bad_job_still_runs_backup(self):
        with patch.object(wrapper, "PRIVATE", Path(self.tmp.name)), \
             patch.object(wrapper, "LOCK", Path(self.tmp.name) / "scheduler.lock"), \
             patch.object(wrapper, "SUCCESS", self.receipt), \
             patch.object(wrapper, "run_step", side_effect=[False, True, True, True]) as run, \
             patch.object(wrapper, "already_verified_today", side_effect=[False, True]):
            self.assertEqual(wrapper.run_all(), 1)
            self.assertEqual(run.call_count, 4)
            self.assertEqual(run.call_args.args[0], "encrypted_backup")


if __name__ == "__main__":
    unittest.main()
