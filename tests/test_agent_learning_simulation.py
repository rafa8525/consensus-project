"""Read-only sandbox simulations of EXISTING learning, knowledge and repair agents.

These tests document actual current behaviors; they are not claims of feature
readiness. Every write is redirected to a temporary directory. No network,
credentials, Twilio, or live PythonAnywhere paths are used.
"""
from __future__ import annotations
import contextlib
import importlib.util
import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load_module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ExistingAgentFeatureSimulation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.learning = load_module("tools/agent_evolution_cycle.py", "sim_learning")
        self.knowledge = load_module("tools/knowledge_sharing_validator.py", "sim_knowledge")
        self.repair = load_module("tools/agent_self_repair_loop.py", "sim_repair")
        self.learning.LOG_PATH = str(self.root / "evolution.log")
        self.learning.PREDICTIVE_JSON = str(self.root / "predictive_summary.json")
        self.knowledge.CKB_FILE = str(self.root / "centralized_knowledge_base.txt")
        self.knowledge.LOG_FILE = str(self.root / "knowledge.log")
        self.knowledge.AGENT_DIR = str(self.root / "agents")
        self.repair.SUMMARY = str(self.root / "agent_evolution_summary.json")
        self.repair.AGENT_DIR = str(self.root / "agents")
        self.repair.LOG_FILE = str(self.root / "repair.log")
    def invoke(self, fn):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = fn()
        return result, output.getvalue()
    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    # LEARNING: demonstrate false positive and fabricated metrics.
    def test_learning_no_evidence_still_claims_agents_above_threshold(self):
        ret, out = self.invoke(self.learning.main)
        self.assertIsNone(ret)
        self.assertIn("All agents performing above threshold.", out)
        self.assertFalse((self.root / "agent_evolution_summary.json").exists())
    def test_learning_same_input_produces_different_metrics(self):
        self.put("predictive_summary.json", json.dumps({"scores": {"ACS-04": 11}}))
        with patch.object(self.learning.random, "uniform", side_effect=[75.0, 4.5]):
            _, a = self.invoke(self.learning.main)
        with patch.object(self.learning.random, "uniform", side_effect=[90.0, 6.0]):
            _, b = self.invoke(self.learning.main)
        self.assertIn("Predictive-driven optimization engaged: ACS-04", a)
        self.assertIn("Predictive-driven optimization engaged: ACS-04", b)
        self.assertIn("75.00", a)
        self.assertIn("90.00", b)
    def test_learning_corrupt_predictive_json_raises(self):
        self.put("predictive_summary.json", "{invalid")
        with self.assertRaises(json.JSONDecodeError):
            self.learning.main()

    # KNOWLEDGE: current checks are proxies, not actual cross-agent exchange.
    def test_knowledge_large_garbage_and_recent_log_claims_sync(self):
        self.put("centralized_knowledge_base.txt", "Z" * 200)
        self.put("agents/ACS-01.log", "heartbeat only\n")
        ret, out = self.invoke(self.knowledge.main)
        self.assertIsNone(ret)
        self.assertIn("Knowledge Base synchronization validated successfully", out)
    def test_knowledge_missing_base_reports_attention_but_success_return(self):
        self.put("agents/ACS-01.log", "heartbeat only\n")
        ret, out = self.invoke(self.knowledge.main)
        self.assertIsNone(ret)
        self.assertIn("ATTENTION REQUIRED", out)
    def test_knowledge_stale_agent_logs_detected(self):
        import os
        self.put("centralized_knowledge_base.txt", "Z" * 200)
        log = self.put("agents/ACS-01.log", "stale heartbeat\n")
        os.utime(log, (time.time() - 26*3600, time.time() - 26*3600))
        _, out = self.invoke(self.knowledge.main)
        self.assertIn("No agent knowledge updates in the last 24 hours", out)

    # REPAIR: demonstrate log overwrite, missing summary, and no source repair.
    def test_repair_weak_agent_reinitializes_log_not_agent_source(self):
        self.put("agent_evolution_summary.json",
                 json.dumps([{"agent": "ACS-02.log", "score": 64}]))
        agent_log = self.put("agents/ACS-02.log", "valuable original diagnostics\n")
        source = self.put("production/ACS-02.py", "print('unchanged')\n")
        with patch.object(self.repair.time, "sleep", return_value=None):
            ret, out = self.invoke(self.repair.main)
        self.assertIsNone(ret)
        self.assertIn("successfully re-initialized", out)
        self.assertNotIn("valuable original diagnostics", agent_log.read_text())
        self.assertEqual(source.read_text(), "print('unchanged')\n")
    def test_repair_missing_summary_claims_success_return(self):
        ret, out = self.invoke(self.repair.main)
        self.assertIsNone(ret)
        self.assertIn("No evolution summary found", out)
    def test_repair_malformed_summary_raises(self):
        self.put("agent_evolution_summary.json", '{"agents": []}')
        with self.assertRaises(TypeError):
            self.repair.main()
    def test_repair_without_weak_agents_preserves_logs(self):
        self.put("agent_evolution_summary.json",
                 json.dumps([{"agent": "ACS-02.log", "score": 98}]))
        agent_log = self.put("agents/ACS-02.log", "original diagnostics\n")
        _, out = self.invoke(self.repair.main)
        self.assertIn("No agents need repair", out)
        self.assertEqual(agent_log.read_text(), "original diagnostics\n")

if __name__ == "__main__":
    unittest.main()
