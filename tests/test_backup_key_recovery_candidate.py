"""Offline key recovery rehearsal against synthetic backup data only.

No actual private keys, remote storage, or PythonAnywhere files are accessed.
"""
import os
import tempfile
import unittest
from pathlib import Path
from tools import secure_backup_transport_candidate as secure


class OfflineKeyRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.primary_dir = self.base / "live-key-store"
        self.offline_dir = self.base / "offline-key-store"
        self.primary_dir.mkdir(mode=0o700)
        self.offline_dir.mkdir(mode=0o700)
        self.primary = self.primary_dir / "backup.key"
        self.offline = self.offline_dir / "backup.key"
        self.primary.write_bytes(os.urandom(32))
        self.primary.chmod(0o600)
        self.offline.write_bytes(self.primary.read_bytes())
        self.offline.chmod(0o600)

    def test_offline_copy_decrypts_after_primary_lost(self):
        plain = b"synthetic ACS backup payload"
        cipher = secure.encrypt(plain, secure.key_bytes(self.primary))
        self.primary.unlink()
        self.assertEqual(secure.decrypt(cipher, secure.key_bytes(self.offline)), plain)

    def test_key_loss_prevents_restore(self):
        cipher = secure.encrypt(b"synthetic", secure.key_bytes(self.primary))
        self.primary.unlink()
        self.offline.unlink()
        with self.assertRaises(ValueError):
            secure.key_bytes(self.offline)
        with self.assertRaises(Exception):
            secure.decrypt(cipher, os.urandom(32))

    def test_corrupted_offline_key_rejected(self):
        cipher = secure.encrypt(b"synthetic", secure.key_bytes(self.primary))
        self.offline.write_bytes(os.urandom(32))
        with self.assertRaises(Exception):
            secure.decrypt(cipher, secure.key_bytes(self.offline))

    def test_offline_key_permissions_enforced(self):
        self.offline.chmod(0o644)
        with self.assertRaises(PermissionError):
            secure.key_bytes(self.offline)

    def test_offline_key_missing_rejected(self):
        self.offline.unlink()
        with self.assertRaises(ValueError):
            secure.key_bytes(self.offline)


if __name__ == "__main__":
    unittest.main()
