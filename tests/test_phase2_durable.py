"""SQLite journal: restart, replay prevention, and interruption evidence."""
import os
import tempfile
import unittest

from agents.phase2_durable import DurableTaskJournal, DurableSimulatedRouter
from agents.phase2_protocol import ProtocolError


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tempdir.name, "mock_tasks.sqlite")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_durable_journal_requires_simulation(self):
        with self.assertRaises(ProtocolError):
            DurableTaskJournal(self.path)

    def test_completed_task_does_not_rerun_after_restart(self):
        calls = []
        handlers = {"executor": lambda task: calls.append(task) or "done"}
        first = DurableSimulatedRouter(self.path, handlers, simulation=True)
        self.assertEqual(first.dispatch("task1", "executor", "sample")["state"], "completed")
        first.close()
        second = DurableSimulatedRouter(self.path, handlers, simulation=True)
        replay = second.dispatch("task1", "executor", "sample")
        self.assertEqual(replay["state"], "completed")
        self.assertFalse(replay["executed"])
        self.assertEqual(calls, ["sample"])
        second.close()

    def test_interrupted_running_task_becomes_uncertain(self):
        journal = DurableTaskJournal(self.path, simulation=True)
        journal.register("task1", "executor", "sample")
        journal.claim("task1")
        journal.close()  # simulate process disappearance after claim
        calls = []
        restarted = DurableSimulatedRouter(
            self.path, {"executor": lambda task: calls.append(task) or "done"},
            simulation=True)
        replay = restarted.dispatch("task1", "executor", "sample")
        self.assertEqual(replay["state"], "uncertain")
        self.assertFalse(replay["executed"])
        self.assertEqual(calls, [])
        restarted.close()

    def test_pending_task_survives_journal_restart(self):
        journal = DurableTaskJournal(self.path, simulation=True)
        self.assertEqual(journal.register("task1", "executor", "sample"), "registered")
        journal.close()
        reopened = DurableTaskJournal(self.path, simulation=True)
        self.assertEqual(reopened.get("task1")["state"], "pending")
        reopened.close()

    def test_collision_fails_closed_after_restart(self):
        first = DurableSimulatedRouter(
            self.path, {"executor": lambda task: "ok"}, simulation=True)
        first.dispatch("task1", "executor", "sample")
        first.close()
        second = DurableSimulatedRouter(
            self.path, {"executor": lambda task: "ok"}, simulation=True)
        with self.assertRaises(ProtocolError):
            second.dispatch("task1", "executor", "different")
        second.close()

    def test_failure_does_not_replay_after_restart(self):
        calls = []
        def broken(task):
            calls.append(task)
            raise RuntimeError("mock failure")
        first = DurableSimulatedRouter(self.path, {"executor": broken}, simulation=True)
        report = first.dispatch("task1", "executor", "sample")
        self.assertEqual(report["state"], "failed")
        first.close()
        second = DurableSimulatedRouter(self.path, {"executor": broken}, simulation=True)
        self.assertEqual(second.dispatch("task1", "executor", "sample")["state"], "failed")
        self.assertEqual(calls, ["sample"])
        second.close()

    def test_double_claim_rejected(self):
        journal = DurableTaskJournal(self.path, simulation=True)
        journal.register("task1", "executor", "sample")
        journal.claim("task1")
        with self.assertRaises(ProtocolError):
            journal.claim("task1")
        journal.close()

    def test_completion_requires_claim(self):
        journal = DurableTaskJournal(self.path, simulation=True)
        journal.register("task1", "executor", "sample")
        with self.assertRaises(ProtocolError):
            journal.finish("task1", "done", success=True)
        journal.close()

    def test_corrupt_database_is_not_silently_reset(self):
        with open(self.path, "wb") as f:
            f.write(b"not-a-sqlite-database")
        with self.assertRaises(Exception):
            DurableTaskJournal(self.path, simulation=True)


if __name__ == "__main__":
    unittest.main()
