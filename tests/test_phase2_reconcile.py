"""Regression tests for evidence-backed mock task reconciliation."""
import os
import tempfile
import unittest

from agents.phase2_durable import DurableTaskJournal, DurableSimulatedRouter
from agents.phase2_reconcile import UncertainTaskReconciler
from agents.phase2_protocol import ProtocolError


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tempdir.name, "tasks.sqlite")
        self.journal = DurableTaskJournal(self.path, simulation=True)
        self.journal.register("taskA", "executor", "mock action")
        self.journal.claim("taskA")
        self.journal.recover_interrupted()

    def tearDown(self):
        self.journal.close()
        self.tempdir.cleanup()

    def verifier(self, outcome="completed", proof_id="mock-event-42", task_id="taskA"):
        return lambda _id, _task: {"task_id": task_id, "outcome": outcome, "proof_id": proof_id}

    def test_simulation_required(self):
        with self.assertRaises(ProtocolError):
            UncertainTaskReconciler(self.journal, {"executor": self.verifier()})

    def test_success_evidence_closes_without_reexecution(self):
        reconcile = UncertainTaskReconciler(
            self.journal, {"executor": self.verifier()}, simulation=True)
        self.assertEqual(reconcile.reconcile("taskA")["state"], "completed")
        self.assertEqual(self.journal.get("taskA")["result"], "mock-verified:mock-event-42")
        with self.assertRaises(ProtocolError):
            reconcile.reconcile("taskA")

    def test_failure_evidence_closes(self):
        reconcile = UncertainTaskReconciler(
            self.journal, {"executor": self.verifier(outcome="failed")}, simulation=True)
        self.assertEqual(reconcile.reconcile("taskA")["state"], "failed")

    def test_unverifiable_remains_uncertain(self):
        for bad in (None, {}, {"task_id": "wrong", "outcome": "completed", "proof_id": "a"},
                    {"task_id": "taskA", "outcome": "unknown", "proof_id": "a"},
                    {"task_id": "taskA", "outcome": "completed", "proof_id": ""}):
            rec = UncertainTaskReconciler(
                self.journal, {"executor": lambda task_id, task: bad}, simulation=True)
            self.assertEqual(rec.reconcile("taskA")["state"], "uncertain")
            self.assertEqual(self.journal.get("taskA")["state"], "uncertain")

    def test_verifier_exception_remains_uncertain(self):
        def broken(_id, _task):
            raise RuntimeError("secret")
        rec = UncertainTaskReconciler(self.journal, {"executor": broken}, simulation=True)
        report = rec.reconcile("taskA")
        self.assertEqual(report["reason"], "verifier_error")
        self.assertNotIn("secret", str(report))

    def test_missing_verifier_remains_uncertain(self):
        rec = UncertainTaskReconciler(
            self.journal, {"ACS-02": self.verifier()}, simulation=True)
        self.assertEqual(rec.reconcile("taskA")["state"], "uncertain")

    def test_reconciled_task_does_not_replay_after_restart(self):
        rec = UncertainTaskReconciler(
            self.journal, {"executor": self.verifier()}, simulation=True)
        rec.reconcile("taskA")
        self.journal.close()
        self.journal = DurableTaskJournal(self.path, simulation=True)
        calls = []
        router = DurableSimulatedRouter(
            self.path, {"executor": lambda task: calls.append(task) or "done"}, simulation=True)
        report = router.dispatch("taskA", "executor", "mock action")
        self.assertFalse(report["executed"])
        self.assertEqual(report["state"], "completed")
        self.assertEqual(calls, [])
        router.close()

    def test_concurrent_change_rejected(self):
        def change_during_check(task_id, task):
            self.journal.db.execute(
                "UPDATE tasks SET state='failed' WHERE task_id=?", (task_id,))
            return {"task_id": task_id, "outcome": "completed", "proof_id": "mock-evidence"}
        rec = UncertainTaskReconciler(
            self.journal, {"executor": change_during_check}, simulation=True)
        with self.assertRaises(ProtocolError):
            rec.reconcile("taskA")


if __name__ == "__main__":
    unittest.main()
