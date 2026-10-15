"""Isolated ACS-03 source-freshness tests. No production data or credentials."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/fitness_tracking_verifier.py"

class FitnessVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fitness = self.root / "memory/logs/fitness"
        self.fitness.mkdir(parents=True)
        self.source = self.fitness / "daily_metrics.jsonl"
        self.now = datetime.now(timezone.utc)

    def invoke(self):
        env = dict(os.environ, ACS_REPO_ROOT=str(self.root))
        env.pop("CONSENSUS_MEMORY_ROOT", None)
        return subprocess.run([sys.executable, str(SCRIPT)], env=env,
                              text=True, capture_output=True, timeout=10)

    def write(self, record):
        self.source.write_text(json.dumps(record) + "\n")

    def test_missing_source_fails(self):
        self.assertEqual(self.invoke().returncode, 1)

    def test_unrelated_recent_log_cannot_pass(self):
        (self.fitness / "steps.log").write_text("fresh")
        self.assertEqual(self.invoke().returncode, 1)

    def test_empty_source_fails(self):
        self.source.touch()
        self.assertEqual(self.invoke().returncode, 1)

    def test_invalid_json_fails(self):
        self.source.write_text("{")
        self.assertEqual(self.invoke().returncode, 1)

    def test_missing_metric_fails(self):
        self.write({"timestamp": self.now.isoformat()})
        self.assertEqual(self.invoke().returncode, 1)

    def test_stale_record_fails(self):
        self.write({"timestamp": (self.now - timedelta(days=3)).isoformat(), "steps": 500})
        self.assertEqual(self.invoke().returncode, 1)

    def test_future_record_fails(self):
        self.write({"timestamp": (self.now + timedelta(hours=2)).isoformat(), "steps": 500})
        self.assertEqual(self.invoke().returncode, 1)

    def test_recent_record_passes(self):
        self.write({"timestamp": self.now.isoformat(), "steps": 500})
        self.assertEqual(self.invoke().returncode, 0)

    def test_zero_steps_passes(self):
        self.write({"timestamp": self.now.isoformat(), "steps": 0})
        self.assertEqual(self.invoke().returncode, 0)

    def test_string_measurement_fails(self):
        self.write({"timestamp": self.now.isoformat(), "steps": "500"})
        self.assertEqual(self.invoke().returncode, 1)

    def test_naive_timestamp_fails(self):
        self.write({"timestamp": self.now.replace(tzinfo=None).isoformat(), "steps": 500})
        self.assertEqual(self.invoke().returncode, 1)

    def test_symlink_source_fails(self):
        external = self.root / "external.jsonl"
        external.write_text(json.dumps({"timestamp": self.now.isoformat(), "steps": 500}) + "\n")
        self.source.symlink_to(external)
        self.assertEqual(self.invoke().returncode, 1)

    def test_alternate_root(self):
        alt = self.root / "private"
        target = alt / "logs/fitness/daily_metrics.jsonl"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps({"timestamp": self.now.isoformat(), "steps": 2}) + "\n")
        env = dict(os.environ, ACS_REPO_ROOT=str(self.root), CONSENSUS_MEMORY_ROOT=str(alt))
        run = subprocess.run([sys.executable, str(SCRIPT)], env=env,
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0)

if __name__ == "__main__":
    unittest.main()
