"""Four-step isolated simulation: source inventory, baseline, failures, deployment gates."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.agent_performance_baseline import evaluate, simulated_promotion_gate
from agents import run_acs_cycle
from agents.supervisor import Supervisor
from tools import agent_capability_guard, knowledge_sharing_validator

ROOT = Path(__file__).resolve().parents[1]

class AgentFourStepSimulation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "memory/agents").mkdir(parents=True)
        (self.root / "memory/logs/agents").mkdir(parents=True)

    def write_state(self, states=("healthy", "healthy", "healthy", "healthy"), ok=True):
        results = {"self_improve":{"ok":True},"evaluation":{"ok":True}}
        for key, status in zip(("acs_02","acs_03","acs_04","acs_05"), states):
            results[key] = {"ok": status == "healthy", "status": status, "attempt_count": 1}
        import time
        state = {"last_supervisor_status": "ok" if ok else "degraded",
                 "last_supervisor_ts": time.time(), "last_supervisor_results": results}
        (self.root / "memory/agents/state.json").write_text(json.dumps(state))
        return state

    # Step 1: inventory real source contracts rather than invented scores.
    def test_01_source_inventory_uses_existing_supervisor_and_metric_files(self):
        self.assertTrue((ROOT / "agents/core/metrics.py").is_file())
        self.assertTrue((ROOT / "agents/run_acs_cycle.py").is_file())
        self.assertTrue((ROOT / "agents/supervisor.py").is_file())
        self.assertTrue((ROOT / "tools/operational_certification.py").is_file())
        self.assertTrue((ROOT / "tools/agent_capability_guard.py").is_file())

    # Step 2: measure only what existing data warrants.
    def test_02_all_five_agents_current_healthy(self):
        self.write_state()
        data = evaluate(self.root)
        self.assertEqual(set(data["agents"]), {"ACS-01","ACS-02","ACS-03","ACS-04","ACS-05"})
        self.assertTrue(all(a["latest_healthy"] is True for a in data["agents"].values()))
        self.assertTrue(all(a["historical_success_rate"] is None for a in data["agents"].values()))
        self.assertFalse(data["learning_effectiveness_verified"])

    def test_03_missing_state_is_unknown_not_success(self):
        data = evaluate(self.root)
        self.assertTrue(all(a["latest_healthy"] is None for a in data["agents"].values()))
        self.assertIsNone(data["supervisor_metric_history"]["success_rate"])

    def test_04_measured_supervisor_history_not_fabricated_per_agent(self):
        self.write_state()
        p = self.root / "memory/logs/agents/metrics.jsonl"
        p.write_text('{"metric":"supervisor_cycle","status":"ok"}\n'
                     '{"metric":"supervisor_cycle","status":"degraded"}\n'
                     '{"metric":"other"}\n'
                     'bad-json\n'
                     '{"metric":"supervisor_cycle","status":"ok"}\n')
        data = evaluate(self.root)
        self.assertEqual(data["supervisor_metric_history"]["observed_cycles"], 3)
        self.assertEqual(data["supervisor_metric_history"]["success_rate"], 0.6667)
        self.assertEqual(data["supervisor_metric_history"]["unknown_or_invalid"], 1)

    # Step 3: mock actual process boundaries, not synthetic reimplementations.
    def test_05_child_warning_never_classified_healthy(self):
        proc = SimpleNamespace(returncode=1, stdout="", stderr="")
        with patch.object(run_acs_cycle.subprocess, "run", return_value=proc):
            self.assertEqual(run_acs_cycle.run_process("infrastructure_guardian", Path("/simulated"))["status"], "warning")

    def test_06_child_crash_classified_execution_failure(self):
        with patch.object(run_acs_cycle.subprocess, "run", side_effect=TimeoutError("simulated")):
            x = run_acs_cycle.run_process("fitness_tracking_verifier", Path("/simulated"))
        self.assertEqual(x["status"], "execution_failure")

    def test_07_continuity_guardian_corrupt_success_marker_rejected(self):
        proc = SimpleNamespace(returncode=0, stdout="END status=OKAY\n", stderr="")
        with patch.object(run_acs_cycle.subprocess, "run", return_value=proc):
            self.assertEqual(run_acs_cycle.run_process("continuity_guardian", Path("/simulated"))["status"], "execution_failure")

    def test_08_continuity_guardian_valid_marker_healthy(self):
        proc = SimpleNamespace(returncode=0, stdout="END status=OK\n", stderr="")
        with patch.object(run_acs_cycle.subprocess, "run", return_value=proc):
            self.assertEqual(run_acs_cycle.run_process("continuity_guardian", Path("/simulated"))["status"], "healthy")

    def test_09_absorption_failure_stops_success_marker_publication(self):
        with patch.object(run_acs_cycle, "run_process", return_value={"status":"execution_failure"}) as worker:
            output = run_acs_cycle.run_acs02()
        self.assertEqual(worker.call_count, 1)
        self.assertTrue(output[-1]["skipped"])
        self.assertEqual(output[-1]["status"], "execution_failure")

    def test_10_severity_propagates_most_serious_failure(self):
        self.assertEqual(run_acs_cycle.overall_status([
            {"status": "healthy"}, {"status": "warning"}, {"status": "critical"}]), "critical")
        self.assertEqual(run_acs_cycle.overall_status([
            {"status": "healthy"}, {"status": "execution_failure"}]), "execution_failure")

    def test_11_supervisor_recovers_one_transient_child_failure(self):
        good = json.dumps({"agent":"ACS-03","status":"healthy"})
        responses = [
            SimpleNamespace(returncode=1, stdout="", stderr="transient"),
            SimpleNamespace(returncode=0, stdout=good, stderr=""),
        ]
        with patch("agents.supervisor.subprocess.run", side_effect=responses), patch("agents.supervisor.time.sleep"):
            x = Supervisor({})._run_child_cycle("ACS-03")
        self.assertTrue(x["ok"])
        self.assertEqual(x["attempt_count"], 2)

    def test_12_supervisor_repeated_failure_remains_unhealthy(self):
        proc = SimpleNamespace(returncode=1, stdout="", stderr="persistent")
        with patch("agents.supervisor.subprocess.run", return_value=proc), patch("agents.supervisor.time.sleep"):
            x = Supervisor({})._run_child_cycle("ACS-03")
        self.assertFalse(x["ok"])
        self.assertEqual(x["attempt_count"], 2)

    # Step 4: promotion gates must reject failed evidence and preserve files.
    def test_13_proposed_improvement_gate_fails_on_bad_supervisor_evidence(self):
        state = self.write_state(states=("healthy","execution_failure","healthy","healthy"), ok=False)
        path = self.root / "memory/agents/state.json"
        # Existing guard checks only learning + ACS-02; strict promotion checks all five.
        approved, _ = simulated_promotion_gate(evaluate(self.root))
        self.assertFalse(approved)

    def test_13b_all_five_healthy_allows_only_simulated_promotion(self):
        self.write_state()
        approved, explanation = simulated_promotion_gate(evaluate(self.root))
        self.assertTrue(approved)
        self.assertIn("NOT proof of learning", explanation)

    def test_14_baseline_does_not_change_any_production_or_sandbox_file(self):
        self.write_state()
        before = sorted((str(p.relative_to(self.root)), p.read_bytes())
                        for p in self.root.rglob("*") if p.is_file())
        evaluate(self.root)
        after = sorted((str(p.relative_to(self.root)), p.read_bytes())
                       for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(before, after)

    def test_15_no_legacy_repair_or_sms_execution_in_gate(self):
        source = (ROOT / "tools/master_control_loop.py").read_text()
        self.assertNotIn('"agent_self_repair_loop"', source)
        self.assertNotIn('"agent_evolution_cycle"', source)
        self.assertNotIn('twilio_guard.send_sms', (ROOT / "tools/agent_performance_baseline.py").read_text())
        self.assertNotIn('subprocess.run(', (ROOT / "tools/agent_performance_baseline.py").read_text())

if __name__ == "__main__":
    unittest.main()
