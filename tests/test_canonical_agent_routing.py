"""Sandbox regressions for canonical ACS capability routing."""
import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tools import agent_capability_guard, knowledge_sharing_validator

class CanonicalRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.time = datetime.now(timezone.utc)
        self.state = self.root / "state.json"
        self.marker = self.root / "absorption_last_success.json"
        self.kb = self.root / "centralized_knowledge_base.txt"
        self.state.write_text(json.dumps({
            "last_supervisor_ts": self.time.timestamp(),
            "last_supervisor_results": {
                "self_improve": {"ok": True},
                "evaluation": {"ok": True},
                "acs_02": {"ok": True}
            }
        }))
        self.kb.write_text("Centralized Knowledge Base\n\nGenerated (UTC): " + self.time.isoformat() + "\nentry\n")
        self.marker.write_text(json.dumps({
            "status": "ok",
            "last_success_utc": self.time.isoformat(),
            "centralized_knowledge_base_size_bytes": self.kb.stat().st_size
        }))
    def test_agent_canonical_evidence_healthy(self):
        self.assertTrue(agent_capability_guard.evaluate(self.state, self.time.timestamp())[0])
    def test_agent_rejects_false_improvement_claim(self):
        data = json.loads(self.state.read_text())
        data["last_supervisor_results"]["self_improve"]["ok"] = False
        self.state.write_text(json.dumps(data))
        self.assertFalse(agent_capability_guard.evaluate(self.state, self.time.timestamp())[0])
    def test_agent_rejects_stale_state(self):
        self.assertFalse(agent_capability_guard.evaluate(self.state, self.time.timestamp()+37*3600)[0])
    def test_knowledge_canonical_healthy(self):
        self.assertTrue(knowledge_sharing_validator.evaluate(self.marker, self.kb, self.time)[0])
    def test_knowledge_rejects_fake_big_text(self):
        self.kb.write_text("X"*500)
        self.assertFalse(knowledge_sharing_validator.evaluate(self.marker, self.kb, self.time)[0])
    def test_knowledge_rejects_wrong_marker_size(self):
        data=json.loads(self.marker.read_text())
        data["centralized_knowledge_base_size_bytes"]=123456
        self.marker.write_text(json.dumps(data))
        self.assertFalse(knowledge_sharing_validator.evaluate(self.marker, self.kb, self.time)[0])
    def test_knowledge_rejects_stale_marker(self):
        self.assertFalse(knowledge_sharing_validator.evaluate(self.marker, self.kb, self.time+timedelta(hours=37))[0])
    def test_mcl_does_not_invoke_legacy_mutating_repair(self):
        src=(Path(__file__).resolve().parents[1]/"tools/master_control_loop.py").read_text()
        self.assertNotIn('"agent_self_repair_loop"', src)
        self.assertNotIn('"agent_evolution_cycle"', src)
        self.assertIn('"agent_capability_guard"', src)
        self.assertIn('automatic log rewriting disabled', src)
if __name__ == "__main__":
    unittest.main()
