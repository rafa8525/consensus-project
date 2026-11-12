"""Privacy-safe ACS-03 local diagnostic, no runtime mutations."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.acs03_readonly_diagnose import summarize

class ACS03ReadOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.root = self.home / "consensus-project"
        self.state = self.root / "memory/agents/acs03_state.json"
        self.state.parent.mkdir(parents=True)

    def test_missing_sources_are_reported_not_faked(self):
        result = summarize(self.root, self.home)
        self.assertFalse(result["checks"]["fitness_source_present"])
        self.assertFalse(result["checks"]["state_valid"])

    def test_sensitive_subprocess_output_not_printed(self):
        self.state.write_text(json.dumps({
            "status": "execution_failure",
            "results": [
                {"component": "fitness_tracking_verifier", "status": "execution_failure",
                 "returncode": 1, "stdout": "private-health-record-abc",
                 "stderr": "secret-token-xyz"},
                {"status": "execution_failure", "returncode": 2, "error": "sensitive-data"},
            ]
        }))
        result = summarize(self.root, self.home)
        self.assertTrue(result["checks"]["state_valid"])
        self.assertEqual(result["state"]["unexpected_component_count"], 1)
        self.assertEqual(result["state"]["results"][1]["component"], "unexpected_or_unnamed")
        output = json.dumps(result)
        for value in ("private-health-record-abc","secret-token-xyz","sensitive-data"):
            self.assertNotIn(value, output)

    def test_missing_cloud_script_not_misreported_as_healthy(self):
        report = summarize(self.root, self.home)
        self.assertFalse(report["checks"]["cloud_cycle_script_present"])

    def test_original_source_is_not_modified(self):
        source = self.root / "memory/logs/fitness/daily_metrics.jsonl"
        source.parent.mkdir(parents=True)
        content = '{"timestamp":"2026-11-12T00:00:00Z","steps":100}\n'
        source.write_text(content)
        before = source.stat().st_mtime_ns
        report = summarize(self.root, self.home)
        self.assertTrue(report["checks"]["fitness_source_present"])
        self.assertEqual(source.read_text(), content)
        self.assertEqual(source.stat().st_mtime_ns, before)

if __name__ == "__main__":
    unittest.main()
