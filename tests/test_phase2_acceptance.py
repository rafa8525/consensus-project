"""End-to-end Phase 2 acceptance: mock-only workflow, restart and reconciliation.

Acceptance scope is deterministic, isolated simulation. No production scheduler,
external API, or actual process termination is exercised by this suite.
"""
import os
import tempfile
import unittest

from agents.phase2_router import SimulatedRouter
from agents.phase2_durable import DurableTaskJournal, DurableSimulatedRouter
from agents.phase2_reconcile import UncertainTaskReconciler
from agents.phase2_protocol import ProtocolError


class Phase2EndToEndAcceptance(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.folder.name, "phase2_acceptance.sqlite")

    def tearDown(self):
        self.folder.cleanup()

    def test_01_two_agents_execute_and_duplicates_are_blocked(self):
        counts = {"executor": 0, "ACS-02": 0}
        def executor(task):
            counts["executor"] += 1
            return "mock execution success"
        def knowledge(task):
            counts["ACS-02"] += 1
            return "mock knowledge success"
        router = SimulatedRouter(
            {"executor": executor, "ACS-02": knowledge}, simulation=True)
        first = router.dispatch("task-exec", "executor", "mock task A")
        second = router.dispatch("task-knowledge", "ACS-02", "mock task B")
        self.assertEqual(first["execution_status"], "completed")
        self.assertEqual(second["execution_status"], "completed")
        self.assertEqual(first["ack_status"], "accepted")
        self.assertEqual(second["ack_status"], "accepted")
        self.assertTrue(router.dispatch("task-exec", "executor", "mock task A")["duplicate"])
        self.assertEqual(counts, {"executor": 1, "ACS-02": 1})

    def test_02_interruption_restart_reconciliation_and_no_replay(self):
        # Persist a claimed task as if the process stopped after beginning work.
        journal = DurableTaskJournal(self.db_path, simulation=True)
        journal.register("task-crash", "executor", "mock external operation")
        journal.claim("task-crash")
        journal.close()
        called = []
        restarted = DurableSimulatedRouter(
            self.db_path, {"executor": lambda task: called.append(task) or "done"},
            simulation=True)
        self.assertEqual(restarted.journal.get("task-crash")["state"], "uncertain")
        held = restarted.dispatch("task-crash", "executor", "mock external operation")
        self.assertFalse(held["executed"])
        self.assertEqual(called, [])
        verified = UncertainTaskReconciler(
            restarted.journal,
            {"executor": lambda task_id, task: {
                "task_id": task_id, "outcome": "completed", "proof_id": "mock-proof-100"
            }}, simulation=True)
        self.assertEqual(verified.reconcile("task-crash")["state"], "completed")
        restarted.close()
        third = DurableSimulatedRouter(
            self.db_path, {"executor": lambda task: called.append(task) or "done"},
            simulation=True)
        again = third.dispatch("task-crash", "executor", "mock external operation")
        self.assertEqual(again["state"], "completed")
        self.assertFalse(again["executed"])
        self.assertEqual(called, [])
        third.close()

    def test_03_missing_evidence_cannot_certify_work(self):
        journal = DurableTaskJournal(self.db_path, simulation=True)
        journal.register("task-unclear", "executor", "mock operation")
        journal.claim("task-unclear")
        journal.close()
        called = []
        restarted = DurableSimulatedRouter(
            self.db_path, {"executor": lambda task: called.append(task) or "done"},
            simulation=True)
        reconcile = UncertainTaskReconciler(
            restarted.journal, {"executor": lambda task_id, task: None},
            simulation=True)
        self.assertEqual(reconcile.reconcile("task-unclear")["state"], "uncertain")
        replay = restarted.dispatch("task-unclear", "executor", "mock operation")
        self.assertEqual(replay["state"], "uncertain")
        self.assertFalse(replay["executed"])
        self.assertEqual(called, [])
        restarted.close()

    def test_04_failed_mock_action_does_not_retry_on_restart(self):
        calls = []
        def fail(task):
            calls.append(task)
            raise RuntimeError("private error")
        first = DurableSimulatedRouter(
            self.db_path, {"executor": fail}, simulation=True)
        result = first.dispatch("task-failed", "executor", "mock operation")
        self.assertEqual(result["state"], "failed")
        first.close()
        next_instance = DurableSimulatedRouter(
            self.db_path, {"executor": fail}, simulation=True)
        report = next_instance.dispatch("task-failed", "executor", "mock operation")
        self.assertEqual(report["state"], "failed")
        self.assertFalse(report["executed"])
        self.assertEqual(len(calls), 1)
        next_instance.close()

    def test_05_unauthorized_reconciliation_and_collision_rejected(self):
        journal = DurableTaskJournal(self.db_path, simulation=True)
        journal.register("task-1", "executor", "mock operation")
        journal.claim("task-1")
        journal.recover_interrupted()
        reconcile = UncertainTaskReconciler(
            journal, {"ACS-02": lambda task_id, task: {
                "task_id": task_id, "outcome": "completed", "proof_id": "test"
            }}, simulation=True)
        self.assertEqual(reconcile.reconcile("task-1")["state"], "uncertain")
        with self.assertRaises(ProtocolError):
            journal.register("task-1", "executor", "different operation")
        journal.close()


if __name__ == "__main__":
    unittest.main()
