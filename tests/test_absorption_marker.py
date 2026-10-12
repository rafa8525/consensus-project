"""ACS-02 marker regression tests using only temporary files."""
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import write_absorption_public_marker as marker


class AbsorptionMarkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.kb = self.root / "centralized_knowledge_base.txt"
        self.public = self.root / "public"
        self.out = self.public / "absorption_last_success.json"
        self.patches = [
            patch.object(marker, "CKB_PATH", self.kb),
            patch.object(marker, "PUBLIC_DIR", self.public),
            patch.object(marker, "MARKER_PATH", self.out),
            patch.object(marker, "get_git_commit", return_value="test"),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def create_kb(self, text=None):
        self.kb.write_text(text or (
            "Centralized Knowledge Base\n\nGenerated (UTC): "
            "2026-10-11T00:00:00+00:00\nMemory Root: test\n\nData\n"
        ))

    def test_fresh_knowledge_base_without_movie_export_succeeds(self):
        self.create_kb()
        self.assertEqual(marker.main(), 0)
        result = json.loads(self.out.read_text())
        self.assertEqual(result["status"], "ok")
        self.assertIn("centralized_knowledge_base_size_bytes", result)
        self.assertNotIn("export_size_bytes", result)

    def test_missing_knowledge_base_fails(self):
        self.assertEqual(marker.main(), 1)
        self.assertFalse(self.out.exists())

    def test_stale_knowledge_base_fails(self):
        self.create_kb()
        old = time.time() - 3600
        os.utime(self.kb, (old, old))
        self.assertEqual(marker.main(), 1)
        self.assertFalse(self.out.exists())

    def test_future_timestamp_fails(self):
        self.create_kb()
        future = time.time() + 3600
        os.utime(self.kb, (future, future))
        self.assertEqual(marker.main(), 1)

    def test_invalid_content_fails(self):
        self.create_kb("not a knowledge base\n")
        self.assertEqual(marker.main(), 1)


if __name__ == "__main__":
    unittest.main()
