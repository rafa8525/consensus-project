"""Sandbox tests for ACS-03 fitness freshness, using only temporary files."""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "fitness_tracking_verifier.py"

class FitnessVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.fitness = self.base / "memory/logs/fitness"

    def run_verifier(self):
        env = dict(os.environ, ACS_REPO_ROOT=str(self.base))
        return subprocess.run([sys.executable, str(SCRIPT)], env=env, text=True, capture_output=True)

    def test_missing_directory_fails(self):
        p = self.run_verifier()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_empty_directory_fails(self):
        self.fitness.mkdir(parents=True)
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_stale_file_fails(self):
        self.fitness.mkdir(parents=True)
        f = self.fitness / "steps.log"
        f.write_text("steps")
        t = time.time() - 90000
        os.utime(f, (t, t))
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_recent_file_passes(self):
        self.fitness.mkdir(parents=True)
        (self.fitness / "steps.log").write_text("steps")
        self.assertEqual(self.run_verifier().returncode, 0)

    def test_future_dated_file_fails(self):
        self.fitness.mkdir(parents=True)
        f = self.fitness / "steps.log"
        f.write_text("steps")
        t = time.time() + 3600
        os.utime(f, (t, t))
        self.assertEqual(self.run_verifier().returncode, 1)

    def test_symlink_does_not_fake_freshness(self):
        self.fitness.mkdir(parents=True)
        outside = self.base / "outside.log"
        outside.write_text("steps")
        (self.fitness / "latest.log").symlink_to(outside)
        self.assertEqual(self.run_verifier().returncode, 1)

if __name__ == "__main__":
    unittest.main()
