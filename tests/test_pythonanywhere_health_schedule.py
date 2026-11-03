"""Regression checks for integrated PythonAnywhere health publication detection."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "health_bridge", Path(__file__).resolve().parents[1] / "agents" / "pythonanywhere_health_bridge.py"
)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class Response:
    status_code = 200

    def __init__(self, tasks):
        self.tasks = tasks

    def json(self):
        return self.tasks


class ScheduleTests(unittest.TestCase):
    def check(self, tasks, wired=True):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "agents").mkdir()
            (root / "agents" / "supervisor.py").write_text(
                "run_pythonanywhere_health_bridge.sh" if wired else "no bridge"
            )
            (root / "agents" / "run_acs01_supervisor.sh").write_text(
                "python3 -m agents.supervisor" if wired else "echo no supervisor"
            )
            with patch.object(bridge, "REPO", root), \
                 patch.dict(bridge.os.environ, {"API_TOKEN": "test", "USER": "test"}), \
                 patch("requests.get", return_value=Response(tasks)):
                return bridge.pythonanywhere_schedule()

    def test_integrated_enabled(self):
        result = self.check([{"id": 1524414, "enabled": True,
                              "command": "bash agents/run_acs01_supervisor.sh"}])
        self.assertEqual(result["health_task"]["mode"], "acs01_integrated")
        self.assertTrue(result["health_task"]["found"])
        self.assertTrue(result["health_task"]["enabled"])
        self.assertFalse(result["health_task"]["standalone_found"])

    def test_disabled_supervisor_does_not_count(self):
        result = self.check([{"id": 1, "enabled": False,
                              "command": "bash agents/run_acs01_supervisor.sh"}])
        self.assertFalse(result["health_task"]["found"])

    def test_missing_wiring_does_not_count(self):
        result = self.check([{"id": 1, "enabled": True,
                              "command": "bash agents/run_acs01_supervisor.sh"}], wired=False)
        self.assertFalse(result["health_task"]["found"])

    def test_standalone_still_supported(self):
        result = self.check([{"id": 2, "enabled": True,
                              "command": "bash agents/run_pythonanywhere_health_bridge.sh"}])
        self.assertEqual(result["health_task"]["mode"], "standalone")
        self.assertTrue(result["health_task"]["standalone_found"])

    def test_no_tasks_still_alerts(self):
        result = self.check([])
        self.assertFalse(result["health_task"]["found"])
        self.assertFalse(result["health_task"]["enabled"])


if __name__ == "__main__":
    unittest.main()
