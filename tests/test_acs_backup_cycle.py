import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import run_acs_backup_cycle as runner


class BackupCycleGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.private = self.home / ".secrets/google"
        self.private.mkdir(parents=True)
        (self.private / "drive_backup_folder_id.txt").write_text("safe-folder-id\n")

    def test_verified_success_writes_receipt(self):
        evidence = {"status":"uploaded_verified", "file_count":34,
                    "restore_verified":True, "remote_id":"item",
                    "encrypted_sha256":"a"*64, "finished_at_utc":"2026-10-08T21:00:00+00:00"}
        def fake_execute(root, plain, cipher, key, token, folder):
            plain.parent.mkdir(parents=True, exist_ok=True)
            plain.write_bytes(b"temporary")
            self.assertEqual(folder, "safe-folder-id")
            return evidence
        with patch.object(runner, "execute", side_effect=fake_execute):
            result = runner.cycle(self.home)
        self.assertEqual(result["status"], "uploaded_verified")
        self.assertFalse(list((self.home / "local_backups/acs").glob("*.zip")))
        receipt = self.private / "acs_backup_success.json"
        self.assertEqual(json.loads(receipt.read_text()), evidence)
        self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)

    def test_failure_does_not_publish_success(self):
        with patch.object(runner, "execute", side_effect=RuntimeError("injected outage")):
            with self.assertRaises(RuntimeError):
                runner.cycle(self.home)
        self.assertFalse((self.private / "acs_backup_success.json").exists())

    def test_bad_folder_id_fails_closed(self):
        (self.private / "drive_backup_folder_id.txt").write_text("bad folder id")
        with patch.object(runner, "execute") as execute:
            with self.assertRaises(ValueError):
                runner.cycle(self.home)
            execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
