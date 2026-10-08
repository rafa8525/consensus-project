import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from agents.backup_health import evaluate


class BackupHealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "receipt.json"
        self.now = datetime(2026, 10, 8, 21, 0, tzinfo=timezone.utc)

    def save(self, age_hours=1, **kwargs):
        record = {
            "status": "uploaded_verified",
            "restore_verified": True,
            "file_count": 34,
            "remote_id": "test-file",
            "encrypted_sha256": "f" * 64,
            "finished_at_utc": (self.now - timedelta(hours=age_hours)).isoformat(),
        }
        record.update(kwargs)
        self.path.write_text(json.dumps(record))

    def test_missing(self):
        self.assertEqual(evaluate(self.path, self.now)["status"], "critical")

    def test_recent_verified(self):
        self.save()
        self.assertTrue(evaluate(self.path, self.now)["ok"])

    def test_stale(self):
        self.save(age_hours=37)
        self.assertFalse(evaluate(self.path, self.now)["ok"])

    def test_missing_restore_proof(self):
        self.save(restore_verified=False)
        self.assertFalse(evaluate(self.path, self.now)["ok"])

    def test_bad_integrity_hash(self):
        self.save(encrypted_sha256="invalid")
        self.assertFalse(evaluate(self.path, self.now)["ok"])

    def test_future_timestamp(self):
        self.save(age_hours=-2)
        self.assertFalse(evaluate(self.path, self.now)["ok"])

    def test_corrupt(self):
        self.path.write_text("{")
        self.assertFalse(evaluate(self.path, self.now)["ok"])


if __name__ == "__main__":
    unittest.main()
