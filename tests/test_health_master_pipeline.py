import unittest
from unittest.mock import patch, SimpleNamespace
from tools import health_master

class HealthMasterPipelineTests(unittest.TestCase):
    def test_success(self):
        with patch.object(health_master.subprocess, "run", return_value=SimpleNamespace(returncode=0)):
            health_master.run("fitness_progress_master.py")

    def test_failure(self):
        with patch.object(health_master.subprocess, "run", return_value=SimpleNamespace(returncode=2)):
            with patch.object(health_master, "log_heartbeat"):
                with self.assertRaises(RuntimeError):
                    health_master.run("nutrition_pipeline.py")

    def test_launch_failure(self):
        with patch.object(health_master.subprocess, "run", side_effect=OSError("missing")):
            with patch.object(health_master, "log_heartbeat"):
                with self.assertRaises(RuntimeError):
                    health_master.run("nutrition_pipeline.py")
