"""Evidence-based historical learning assessment simulations using existing ACS paths."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from tools.learning_effectiveness import assess
from tools.agent_performance_baseline import evaluate
from agents import supervisor

class LearningHistorySimulation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.agent_dir = self.root / "memory/logs/agents"
        self.evidence_dir = self.agent_dir / "learning_evidence"
        self.evidence_dir.mkdir(parents=True)
        self.t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        (self.root / "memory/agents").mkdir(parents=True)

    def record(self, phase, ordinal, passed, *, change="change-123", scenario="same-check"):
        path = self.evidence_dir / f"{phase}_{ordinal}.json"
        path.write_text(json.dumps({"phase": phase, "ordinal": ordinal, "passed": passed}))
        row = {
            "agent": "ACS-03", "change_id": change,
            "scenario_id": scenario, "phase": phase, "passed": passed,
            "evaluated_at_utc": (self.t0 + timedelta(days=0 if phase=="before" else 7,
                                                    minutes=ordinal)).isoformat(),
            "evidence_path": str(path.relative_to(self.root)),
            "evidence_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        with (self.agent_dir / "learning_evaluations.jsonl").open("a") as h:
            h.write(json.dumps(row) + "\n")
        return row

    def test_no_historical_evidence_never_claims_learning(self):
        output = assess(self.root)
        self.assertFalse(output["learning_effectiveness_verified"])
        self.assertEqual(output["evaluated_scenarios"], 0)

    def test_three_before_three_after_successful_comparison(self):
        for i in range(3):
            self.record("before", i, False)
            self.record("after", i, True)
        output = assess(self.root)
        self.assertTrue(output["learning_effectiveness_verified"])
        item=output["assessments"][0]
        self.assertEqual(item["before_pass_rate"], 0.0)
        self.assertEqual(item["after_pass_rate"], 1.0)
        self.assertEqual(item["status"], "observed_improvement")

    def test_repeated_same_artifact_not_counted_as_independent(self):
        row = self.record("before", 0, False)
        with (self.agent_dir / "learning_evaluations.jsonl").open("a") as h:
            h.write(json.dumps(row) + "\n")
            h.write(json.dumps(row) + "\n")
        for i in range(3):
            self.record("after", i, True)
        result=assess(self.root)
        self.assertFalse(result["learning_effectiveness_verified"])
        self.assertEqual(result["assessments"][0]["before_samples"], 1)

    def test_tampered_evidence_rejected(self):
        for i in range(3):
            self.record("before", i, False)
            self.record("after", i, True)
        (self.evidence_dir / "after_0.json").write_text("tampered")
        output=assess(self.root)
        self.assertFalse(output["learning_effectiveness_verified"])
        self.assertEqual(output["assessments"][0]["evidence_rejected"], 1)

    def test_no_improvement_does_not_pass(self):
        for i in range(3):
            self.record("before", i, True)
            self.record("after", i, False)
        self.assertFalse(assess(self.root)["learning_effectiveness_verified"])

    def test_out_of_order_change_does_not_pass(self):
        for i in range(3):
            self.record("before", i, False)
            self.record("after", i, True)
        p = self.agent_dir / "learning_evaluations.jsonl"
        items = [json.loads(line) for line in p.read_text().splitlines()]
        for item in items:
            item["evaluated_at_utc"] = (self.t0 + timedelta(days=7 if item["phase"]=="before" else 0)).isoformat()
        p.write_text("".join(json.dumps(v)+"\n" for v in items))
        self.assertFalse(assess(self.root)["learning_effectiveness_verified"])

    def test_missing_agent_metrics_not_backfilled(self):
        data=evaluate(self.root)
        self.assertTrue(all(v["observations"]==0 for v in data["per_agent_metric_history"].values()))

    def test_per_agent_observations_are_independent(self):
        p=self.agent_dir/"metrics.jsonl"
        p.write_text("\n".join(json.dumps(v) for v in [
            {"metric":"agent_cycle_outcome","agent":"ACS-02","status":"healthy"},
            {"metric":"agent_cycle_outcome","agent":"ACS-02","status":"critical"},
            {"metric":"agent_cycle_outcome","agent":"ACS-03","status":"healthy"},
            {"metric":"supervisor_cycle","status":"ok"}])+"\n")
        result=evaluate(self.root)["per_agent_metric_history"]
        self.assertEqual(result["ACS-02"]["success_rate"], 0.5)
        self.assertEqual(result["ACS-03"]["success_rate"], 1.0)
        self.assertIsNone(result["ACS-04"]["success_rate"])

    def test_supervisor_source_appends_minimal_metrics(self):
        src = Path(supervisor.__file__).read_text()
        self.assertIn('record("agent_cycle_outcome", agent="ACS-01"', src)
        self.assertIn('agent=agent,', src)
        self.assertNotIn('record("agent_cycle_outcome", result=', src)

    def test_evidence_analysis_is_read_only(self):
        self.record("before", 0, False)
        before = sorted((str(p.relative_to(self.root)),p.read_bytes()) for p in self.root.rglob("*") if p.is_file())
        assess(self.root)
        evaluate(self.root)
        after = sorted((str(p.relative_to(self.root)),p.read_bytes()) for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(before, after)

if __name__=="__main__":
    unittest.main()
