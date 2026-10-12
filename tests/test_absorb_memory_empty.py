"""ACS-02 absorption regression: zero-index runs never replace previous output."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import absorb_memory as worker

class AbsorptionWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "memory"
        self.root.mkdir()
        self.output = self.root / "centralized_knowledge_base.txt"
        self.patch = patch.object(worker, "memory_root", return_value=self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_empty_memory_fails_and_preserves_prior_output(self):
        self.output.write_text("existing knowledge")
        self.assertEqual(worker.absorb_memory(), 1)
        self.assertEqual(self.output.read_text(), "existing knowledge")
        self.assertFalse((self.root / "centralized_knowledge_base.txt.tmp").exists())

    def test_single_source_file_succeeds(self):
        (self.root / "source.txt").write_text("new input")
        self.assertEqual(worker.absorb_memory(), 0)
        result = self.output.read_text()
        self.assertIn("Source:", result)
        self.assertIn("new input", result)

    def test_only_excluded_files_fails(self):
        (self.root / "ignored.json").write_text('{"value":1}')
        self.assertEqual(worker.absorb_memory(), 1)
        self.assertFalse(self.output.exists())

if __name__ == "__main__":
    unittest.main()
