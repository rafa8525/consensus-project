import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/fitness_tracking_verifier.py"

class FitnessVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.folder = self.base / "memory/logs/fitness"
        self.source = self.folder / "daily_metrics.jsonl"

    def run_verifier(self):
        env = dict(os.environ)
        env["ACS_REPO_ROOT"] = str(self.base)
        env["CONSENSUS_MEMORY_ROOT"] = str(self.base / "memory")
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            env=env, capture_output=True, text=True,
            timeout=15,
        )

    def write_record(self, hours=-1, steps=100):
        self.folder.mkdir(parents=True, exist_ok=True)
        timestamp = (
            datetime.now(timezone.utc)
            + timedelta(hours=hours)
        ).isoformat()
        self.source.write_text(
            json.dumps({"timestamp": timestamp, "steps": steps}) + "\n"
        )

    def test_missing_directory_fails(self):
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_empty_directory_fails(self):
        self.folder.mkdir(parents=True)
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_recent_file_passes(self):
        self.write_record()
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stale_file_fails(self):
        self.write_record(hours=-25)
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_future_dated_file_fails(self):
        self.write_record(hours=1)
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_symlink_does_not_fake_freshness(self):
        self.folder.mkdir(parents=True)
        outside = self.base / "outside.jsonl"
        outside.write_text(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "steps": 100
        }) + "\n")
        self.source.symlink_to(outside)
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_text_only_is_not_a_measurement(self):
        self.folder.mkdir(parents=True)
        self.source.write_text("steps\n")
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_boolean_is_not_numeric_measurement(self):
        self.write_record(steps=True)
        self.assertEqual(self.run_verifier().returncode, 1)
