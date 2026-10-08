"""Non-production encrypted transport tests: all cloud operations are mocked."""
import hashlib
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from tools import secure_backup_transport_candidate as secure


class TestSecureTransport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.key = os.urandom(32)
        self.keyfile = self.root / "key"
        self.keyfile.write_bytes(self.key)
        self.keyfile.chmod(0o600)

    def test_round_trip(self):
        data = b"archive\x00contents"
        self.assertEqual(secure.decrypt(secure.encrypt(data, self.key), self.key), data)

    def test_random_nonces(self):
        self.assertNotEqual(secure.encrypt(b"same", self.key), secure.encrypt(b"same", self.key))

    def test_tamper_rejected(self):
        cipher = bytearray(secure.encrypt(b"archive", self.key))
        cipher[-1] ^= 1
        with self.assertRaises(Exception):
            secure.decrypt(bytes(cipher), self.key)

    def test_wrong_key_rejected(self):
        with self.assertRaises(Exception):
            secure.decrypt(secure.encrypt(b"content", self.key), os.urandom(32))

    def test_insecure_key_rejected(self):
        self.keyfile.chmod(0o644)
        with self.assertRaises(PermissionError):
            secure.key_bytes(self.keyfile)

    def test_symlink_key_rejected(self):
        link = self.root / "link"
        link.symlink_to(self.keyfile)
        with self.assertRaises(ValueError):
            secure.key_bytes(link)

    def test_file_encrypt_and_no_overwrite(self):
        source = self.root / "backup.zip"
        source.write_bytes(b"fake backup for encryption unit test")
        dest = self.root / "backup.acsenc"
        result = secure.encrypt_file(source, dest, self.keyfile)
        self.assertEqual(result["status"], "encrypted")
        self.assertEqual(secure.decrypt(dest.read_bytes(), self.key), source.read_bytes())
        self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            secure.encrypt_file(source, dest, self.keyfile)

    def test_reject_plaintext_cloud_upload(self):
        path = self.root / "plaintext.zip"
        path.write_bytes(b"hello")
        with self.assertRaises(ValueError):
            secure.upload_verified(path, None, "folder")

    def test_health_missing(self):
        self.assertEqual(secure.check_health(None)["status"], "critical")

    def test_health_fresh(self):
        now = datetime.now(timezone.utc)
        self.assertEqual(secure.check_health({
            "status": "uploaded_verified",
            "finished_at_utc": now.isoformat()}, now)["status"], "healthy")

    def test_health_stale(self):
        now = datetime.now(timezone.utc)
        self.assertEqual(secure.check_health({
            "status": "uploaded_verified",
            "finished_at_utc": (now - timedelta(hours=48)).isoformat()}, now)["status"], "critical")

    def test_upload_checksum_mismatch(self):
        class Action:
            def execute(self):
                return {"id": "mock", "size": "7", "md5Checksum": "incorrect"}
        class Files:
            def create(self, **kwargs):
                return Action()
        class Service:
            def files(self):
                return Files()
        file = self.root / "test.acsenc"
        file.write_bytes(secure.encrypt(b"test", self.key))
        with patch("googleapiclient.http.MediaFileUpload", return_value=object()):
            with self.assertRaises(RuntimeError):
                secure.upload_verified(file, Service(), "folder")

    def test_upload_checksum_success(self):
        file = self.root / "test.acsenc"
        data = secure.encrypt(b"test", self.key)
        file.write_bytes(data)
        class Action:
            def execute(self):
                return {"id": "mock", "size": str(len(data)),
                        "md5Checksum": hashlib.md5(data).hexdigest()}
        class Files:
            def create(self, **kwargs):
                return Action()
        class Service:
            def files(self):
                return Files()
        with patch("googleapiclient.http.MediaFileUpload", return_value=object()):
            self.assertEqual(secure.upload_verified(file, Service(), "folder")["status"], "uploaded_verified")


    def test_remote_download_verified_and_tampering_rejected(self):
        import io
        import json
        import zipfile
        from tools import verified_backup_candidate as backup
        raw = io.BytesIO()
        data = b"mock agent state"
        manifest = {"files": {"registry/state.json": hashlib.sha256(data).hexdigest()}}
        with zipfile.ZipFile(raw, "w") as z:
            z.writestr("registry/state.json", data)
            z.writestr(backup.MANIFEST, json.dumps(manifest))
        cipher = secure.encrypt(raw.getvalue(), self.key)
        digest = hashlib.sha256(cipher).hexdigest()

        class FakeFiles:
            def get_media(self, fileId):
                if fileId != "remote-1":
                    raise AssertionError("unexpected remote ID")
                return object()
        class FakeDrive:
            def files(self):
                return FakeFiles()
        class FakeDownloader:
            payload = cipher
            def __init__(self, buffer, request):
                self.buffer = buffer
            def next_chunk(self):
                self.buffer.write(self.payload)
                return None, True

        with patch("googleapiclient.http.MediaIoBaseDownload", FakeDownloader):
            success = secure.download_and_verify("remote-1", FakeDrive(), digest,
                                                 self.keyfile, backup)
            self.assertEqual(success["status"], "remote_restore_verified")
            self.assertEqual(success["file_count"], 1)
            with self.assertRaisesRegex(ValueError, "ciphertext hash"):
                secure.download_and_verify("remote-1", FakeDrive(), "0" * 64,
                                           self.keyfile, backup)

if __name__ == "__main__":
    unittest.main()
