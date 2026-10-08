"""Isolated regression tests for verified_backup_candidate (no cloud calls)."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools import verified_backup_candidate as backup


class BackupCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        for source in backup.SOURCES:
            p = self.root / source
            if p.suffix:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("knowledge")
            else:
                p.mkdir(parents=True, exist_ok=True)
                (p / "state.json").write_text('{"ok":true}')
        self.archive = Path(self.temp.name) / "backup.zip"

    def test_success_and_verification(self):
        self.assertEqual(backup.create(self.root, self.archive)["file_count"], 6)
        self.assertEqual(backup.verify(self.archive)["file_count"], 6)

    def test_missing_required_source(self):
        (self.root / backup.SOURCES[-1]).unlink()
        with self.assertRaises(ValueError):
            backup.create(self.root, self.archive)

    def test_empty_required_directory(self):
        (self.root / "registry/state.json").unlink()
        with self.assertRaises(ValueError):
            backup.create(self.root, self.archive)

    def test_corruption_detected(self):
        backup.create(self.root, self.archive)
        self.archive.write_bytes(self.archive.read_bytes()[:20])
        with self.assertRaises(zipfile.BadZipFile):
            backup.verify(self.archive)

    def test_rejects_existing_destination(self):
        self.archive.write_text("existing")
        with self.assertRaises(FileExistsError):
            backup.create(self.root, self.archive)
        self.assertEqual(self.archive.read_text(), "existing")

    def test_secret_filename_excluded(self):
        (self.root / "registry/.env").write_text("DO_NOT_INCLUDE")
        (self.root / "registry/vault.key").write_text("DO_NOT_INCLUDE")
        backup.create(self.root, self.archive)
        with zipfile.ZipFile(self.archive) as z:
            self.assertFalse(any(".env" in n or "vault.key" in n for n in z.namelist()))

    def test_symlink_excluded(self):
        (self.root / "registry/link").symlink_to("/etc/passwd")
        backup.create(self.root, self.archive)
        with zipfile.ZipFile(self.archive) as z:
            self.assertNotIn("registry/link", z.namelist())

    def test_oversize_rejected(self):
        with (self.root / "registry/large.bin").open("wb") as f:
            f.truncate(backup.MAX_FILE_BYTES + 1)
        with self.assertRaises(ValueError):
            backup.create(self.root, self.archive)

    def test_modified_content_detected(self):
        backup.create(self.root, self.archive)
        with zipfile.ZipFile(self.archive) as z:
            entries = {n: z.read(n) for n in z.namelist()}
        entries["registry/state.json"] = b"tampered"
        with zipfile.ZipFile(self.archive, "w") as z:
            for name, data in entries.items():
                z.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            backup.verify(self.archive)


if __name__ == "__main__":
    unittest.main()
