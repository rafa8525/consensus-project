"""Tests for safe ACS-03 bridge diagnostics."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agents import pythonanywhere_health_bridge as bridge


class ACS03DiagnosticsTests(unittest.TestCase):
    def test_component_statuses_only(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "acs03_state.json"
            state.write_text(json.dumps({
                "status": "execution_failure",
                "results": [
                    {"component": "health_master", "status": "execution_failure",
                     "returncode": 1, "stderr": "PRIVATE INFORMATION"},
                    {"component": "backup_fitness", "status": "healthy",
                     "returncode": 0, "stdout": "PRIVATE INFORMATION"}
                ]
            }), encoding="utf-8")
            with patch.dict(bridge.ACS_STATE_FILES, {"ACS-03": state}):
                result = bridge.agent_diagnostics("ACS-03")
            self.assertEqual(result["diagnostics_status"], "available")
            self.assertEqual(result["components"][0]["component"], "health_master")
            self.assertEqual(result["components"][0]["returncode"], 1)
            self.assertNotIn("PRIVATE INFORMATION", json.dumps(result))

    def test_missing_state_fails_transparently(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(bridge.ACS_STATE_FILES, {"ACS-03": Path(folder) / "missing.json"}):
                result = bridge.agent_diagnostics("ACS-03")
            self.assertEqual(result["diagnostics_status"], "missing")

    def test_invalid_state_does_not_fake_success(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "acs03_state.json"
            state.write_text("{invalid", encoding="utf-8")
            with patch.dict(bridge.ACS_STATE_FILES, {"ACS-03": state}):
                result = bridge.agent_diagnostics("ACS-03")
            self.assertEqual(result["diagnostics_status"], "unreadable")


if __name__ == "__main__":
    unittest.main()
