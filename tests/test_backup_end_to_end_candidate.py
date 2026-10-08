"""End-to-end mocked Drive encrypted backup/recovery; zero network calls."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import secure_backup_transport_candidate as secure
from tools import verified_backup_candidate as backup


class FakeDrive:
    def __init__(self):
        self.stored = None
    def files(self):
        return self
    def create(self, **kwargs):
        self.upload_file = kwargs["media_body"]
        return self
    def execute(self):
        assert self.stored is not None
        return {"id": "mock-remote-id", "size": str(len(self.stored)),
                "md5Checksum": hashlib.md5(self.stored).hexdigest()}
    def get_media(self, fileId):
        if fileId != "mock-remote-id":
            raise ValueError("unexpected ID")
        return self


class FakeUpload:
    def __init__(self, path, **kwargs):
        self.path = path


class FakeDownload:
    def __init__(self, stream, request):
        self.stream = stream
        self.request = request
    def next_chunk(self):
        self.stream.write(self.request.stored)
        return None, True


class TestEndToEndBackup(unittest.TestCase):
    def test_local_archive_encrypt_upload_download_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "repository"
            for source in backup.SOURCES:
                p = root / source
                if p.suffix:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("synthetic knowledge only")
                else:
                    p.mkdir(parents=True, exist_ok=True)
                    (p / "state.json").write_text('{"status":"synthetic"}')
            archive = base / "acs.zip"
            self.assertEqual(backup.create(root, archive)["file_count"], 5)
            key = base / "key"
            key.write_bytes(os.urandom(32))
            key.chmod(0o600)
            encrypted = base / "acs.acsenc"
            record = secure.encrypt_file(archive, encrypted, key)
            self.assertEqual(secure.verify_encrypted_archive(encrypted, key, backup)["file_count"], 5)
            drive = FakeDrive()
            def fake_upload(path, **kwargs):
                drive.stored = Path(path).read_bytes()
                return FakeUpload(path, **kwargs)
            with patch("googleapiclient.http.MediaFileUpload", fake_upload):
                receipt = secure.upload_verified(encrypted, drive, "mock-folder")
            self.assertEqual(receipt["status"], "uploaded_verified")
            with patch("googleapiclient.http.MediaIoBaseDownload", FakeDownload):
                restored = secure.download_and_verify("mock-remote-id", drive,
                             record["sha256"], key, backup)
            self.assertEqual(restored["file_count"], 5)
            self.assertEqual(restored["status"], "remote_restore_verified")

    def test_backup_stops_on_embedded_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for source in backup.SOURCES:
                p = root / source
                if p.suffix:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("synthetic knowledge")
                else:
                    p.mkdir(parents=True, exist_ok=True)
                    (p / "state.json").write_text("synthetic state")
            (root / "registry" / "credential.txt").write_text(
                "-----BEGIN PRIVATE KEY-----\\nsecret\\n-----END PRIVATE KEY-----"
            )
            with self.assertRaisesRegex(ValueError, "potential credential"):
                backup.create(root, root.parent / "should-not-exist.zip")


if __name__ == "__main__":
    unittest.main()
