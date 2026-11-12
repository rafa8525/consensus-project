"""Guard legacy fitness ingestion against fabricated records."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/fitness_ingest.py"

class LegacyIngestTests(unittest.TestCase):
    def test_fails_closed_without_writing_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            environment = dict(os.environ)
            environment["HOME"] = str(root)
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=root, env=environment, capture_output=True, text=True, timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOCKED:", result.stderr)
            self.assertEqual(list(root.rglob("fitness_data_*.json")), [])
            self.assertEqual(list(root.rglob("daily_metrics.jsonl")), [])

if __name__ == "__main__":
    unittest.main()
