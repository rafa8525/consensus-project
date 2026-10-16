import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "tools/summarize_agent_logs.py"
SPEC = importlib.util.spec_from_file_location("testable_summarizer", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class SummarizerMissingFolderTests(unittest.TestCase):
    def test_missing_optional_folder_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "no_such_optional_folder")
            summaries, index = MODULE.process_dir(missing, "Brainstorm")
            self.assertEqual(summaries, [])
            self.assertEqual(index, [])

    def test_existing_folder_reports_one_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.txt").write_text("Simple note\n")
            summaries, index = MODULE.process_dir(str(folder), "Brainstorm")
            self.assertEqual(len(summaries), 1)
            self.assertEqual(len(index), 1)

if __name__ == "__main__":
    unittest.main()
