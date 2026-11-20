"""End-to-end offline model + SQLite worker queue integration tests.

Run: python3 -m unittest -v test_model_worker_integration.py
"""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from local_inference import fit, load_checkpoint, save_checkpoint
from model_worker import run_model_once
from worker_runtime import connect, enqueue, load_registry, run_once, setup, snapshot

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "agents_registry.json"


class ModelWorkerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "tasks.sqlite"
        self.checkpoint = self.directory / "model.json"
        self.registry = load_registry(REGISTRY)
        self.model = save_checkpoint(self.checkpoint, fit())
        self.con = connect(self.db)
        self.addCleanup(self.con.close)
        setup(self.con)

    def enqueue_task(self, task_id, agent, operation, objective, deps=None):
        enqueue(self.con, self.registry, {
            "id": task_id, "agent_id": agent, "operation": operation,
            "objective": objective, "dependencies": deps or [],
        })

    def test_model_inference_round_trip_and_message(self):
        self.enqueue_task("task1", "AGI-01", "design_experiment",
                          "design benchmark for a new training approach")
        result = run_model_once(self.con, self.registry,
                                load_checkpoint(self.checkpoint), "AGI-01", "worker-1")
        self.assertTrue(result["is_ai_inference"])
        self.assertFalse(result["is_llm"])
        self.assertEqual(result["inference"]["label"], "design_experiment")
        self.assertTrue(result["inference_matches_assigned_operation"])
        self.assertEqual(snapshot(self.con)["tasks"][0]["status"], "done")
        self.assertEqual(snapshot(self.con)["messages"][0]["payload"]["event"], "model_inference_completed")

    def test_dependency_passes_receipt_to_model_worker(self):
        self.enqueue_task("first", "AGI-01", "design_experiment", "plan controlled model experiment")
        self.enqueue_task("second", "AGI-38", "evaluate_evidence",
                          "inspect independent evaluation metrics", ["first"])
        self.assertIsNone(run_model_once(self.con, self.registry, self.model, "AGI-38", "w2"))
        original = run_once(self.con, self.registry, "AGI-01", "w1")
        final = run_model_once(self.con, self.registry, self.model, "AGI-38", "w2")
        self.assertEqual(final["dependency_receipts"][0]["digest"], original["digest"])
        self.assertEqual(len(snapshot(self.con)["messages"]), 2)

    def test_prediction_disagreement_does_not_reassign_task(self):
        self.enqueue_task("different", "AGI-01", "review_hypothesis",
                          "compare validation accuracy with previous results")
        result = run_model_once(self.con, self.registry, self.model, "AGI-01", "w1")
        self.assertEqual(result["operation"], "review_hypothesis")
        self.assertFalse(result["inference_matches_assigned_operation"])
        self.assertEqual(result["inference"]["label"], "evaluate_evidence")

    def test_corrupted_checkpoint_blocks_work(self):
        self.enqueue_task("task1", "AGI-01", "design_experiment", "plan controlled model experiment")
        doc = json.loads(self.checkpoint.read_text())
        doc["model"]["training_count"] = 999
        self.checkpoint.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            load_checkpoint(self.checkpoint)
        self.assertEqual(snapshot(self.con)["tasks"][0]["status"], "queued")

    def test_duplicate_worker_cannot_claim_completed_task(self):
        self.enqueue_task("task1", "AGI-01", "design_experiment", "plan controlled model experiment")
        self.assertIsNotNone(run_model_once(self.con, self.registry, self.model, "AGI-01", "w1"))
        self.assertIsNone(run_model_once(self.con, self.registry, self.model, "AGI-01", "w2"))
        self.assertEqual(len(snapshot(self.con)["messages"]), 1)

    def test_independent_worker_process_cli(self):
        self.enqueue_task("task1", "AGI-01", "design_experiment",
                          "design benchmark for a new training approach")
        p = subprocess.run(
            [sys.executable, str(ROOT / "model_worker.py"), "--db", str(self.db),
             "--registry", str(REGISTRY), "--checkpoint", str(self.checkpoint),
             "--agent", "AGI-01", "--worker-id", "process-1"],
            capture_output=True, text=True, timeout=15, check=True)
        self.assertTrue(json.loads(p.stdout)["is_ai_inference"])
        self.assertEqual(snapshot(self.con)["tasks"][0]["status"], "done")

    def test_unsupported_task_rejected_before_worker(self):
        with self.assertRaises(ValueError):
            self.enqueue_task("bad", "AGI-01", "shell",
                              "execute arbitrary command")

    def test_persisted_results_after_reopen(self):
        self.enqueue_task("task1", "AGI-01", "design_experiment", "plan controlled model experiment")
        run_model_once(self.con, self.registry, self.model, "AGI-01", "w1")
        other = connect(self.db)
        try:
            self.assertEqual(snapshot(other)["tasks"][0]["status"], "done")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
