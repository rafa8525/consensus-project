"""Phase 3 concurrent-memory and durable-workflow acceptance suite."""
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from agents.phase2_durable import DurableTaskJournal
from agents.phase2_protocol import ProtocolError
from agents.phase3_memory import EvidenceMemory
from agents.phase3_pipeline import SimulatedEvidencePipeline


class Phase3IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.task_db = os.path.join(self.tmp.name, "tasks.sqlite")
        self.memory_db = os.path.join(self.tmp.name, "evidence.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_concurrent_writers_distinct_evidence(self):
        # Pre-create the SQLite schema before coordinating writers; otherwise
        # schema initialization can serialize startup and break the barrier.
        initial = EvidenceMemory(self.memory_db, simulation=True)
        initial.close()
        barrier = threading.Barrier(2)
        def writer(i):
            store = EvidenceMemory(self.memory_db, simulation=True)
            try:
                barrier.wait(timeout=15)
                return store.remember("e" + str(i), "task1", "ACS-02",
                                      "mock." + str(i), "finding " + str(i))
            finally:
                store.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(writer, (1, 2)))
        self.assertEqual(results, ["recorded", "recorded"])
        store = EvidenceMemory(self.memory_db, simulation=True)
        self.assertEqual(len(store.for_task("task1")), 2)
        store.close()

    def test_concurrent_same_evidence_id_is_deduplicated(self):
        initial = EvidenceMemory(self.memory_db, simulation=True)
        initial.close()
        barrier = threading.Barrier(2)
        def writer(_):
            store = EvidenceMemory(self.memory_db, simulation=True)
            try:
                barrier.wait(timeout=15)
                return store.remember("e1", "task1", "ACS-02", "mock.1", "same")
            finally:
                store.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(writer, (1, 2)))
        self.assertEqual(sorted(results), ["duplicate", "recorded"])

    def test_completed_task_publishes_evidence_and_replay_does_not_execute(self):
        calls = []
        handlers = {"executor": lambda task: calls.append(task) or "mock result"}
        first = SimulatedEvidencePipeline(
            self.task_db, self.memory_db, handlers, simulation=True)
        one = first.dispatch("task1", "executor", "mock work")
        self.assertEqual((one["state"], one["memory_status"]), ("completed", "recorded"))
        first.close()
        second = SimulatedEvidencePipeline(
            self.task_db, self.memory_db, handlers, simulation=True)
        replay = second.dispatch("task1", "executor", "mock work")
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["memory_status"], "duplicate")
        self.assertEqual(len(second.memory.for_task("task1")), 1)
        self.assertEqual(calls, ["mock work"])
        second.close()

    def test_crash_gap_after_execution_before_memory_reconciles_on_replay(self):
        calls = []
        handlers = {"executor": lambda task: calls.append(task) or "mock complete"}
        # Deliberate simulated crash gap: journal finishes but no memory write occurs.
        from agents.phase2_durable import DurableSimulatedRouter
        worker = DurableSimulatedRouter(self.task_db, handlers, simulation=True)
        self.assertEqual(worker.dispatch("task1", "executor", "mock work")["state"], "completed")
        worker.close()
        pipeline = SimulatedEvidencePipeline(
            self.task_db, self.memory_db, handlers, simulation=True)
        report = pipeline.dispatch("task1", "executor", "mock work")
        self.assertEqual(report["memory_status"], "recorded")
        self.assertFalse(report["executed"])
        self.assertEqual(calls, ["mock work"])
        pipeline.close()

    def test_uncertain_task_never_published_as_success(self):
        journal = DurableTaskJournal(self.task_db, simulation=True)
        journal.register("task1", "executor", "mock work")
        journal.claim("task1")
        journal.close()
        called = []
        pipeline = SimulatedEvidencePipeline(
            self.task_db, self.memory_db,
            {"executor": lambda task: called.append(task) or "done"}, simulation=True)
        report = pipeline.dispatch("task1", "executor", "mock work")
        self.assertEqual(report["state"], "uncertain")
        self.assertEqual(report["memory_status"], "not_recorded")
        self.assertEqual(pipeline.memory.for_task("task1"), [])
        self.assertEqual(called, [])
        pipeline.close()

    def test_conflicting_task_id_is_rejected(self):
        pipeline = SimulatedEvidencePipeline(
            self.task_db, self.memory_db, {"executor": lambda task: "done"}, simulation=True)
        pipeline.dispatch("task1", "executor", "one")
        with self.assertRaises(ProtocolError):
            pipeline.dispatch("task1", "executor", "two")
        pipeline.close()

    def test_simulation_guard(self):
        with self.assertRaises(ProtocolError):
            SimulatedEvidencePipeline(
                self.task_db, self.memory_db, {"executor": lambda task: "done"})


if __name__ == "__main__":
    unittest.main()
