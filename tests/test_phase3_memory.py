"""Phase 3 memory acceptance: provenance, persistence, idempotency, isolation."""
import os
import tempfile
import unittest

from agents.phase3_memory import EvidenceMemory
from agents.phase2_protocol import ProtocolError


class Phase3MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "mock_memory.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def test_simulation_only(self):
        with self.assertRaises(ProtocolError):
            EvidenceMemory(self.path)

    def test_persist_across_restart_with_provenance(self):
        mem = EvidenceMemory(self.path, simulation=True)
        self.assertEqual(mem.remember("e1", "t1", "ACS-02", "mock-run-1", "Test completed"), "recorded")
        mem.close()
        mem = EvidenceMemory(self.path, simulation=True)
        result = mem.for_task("t1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_ref"], "mock-run-1")
        self.assertEqual(result[0]["finding"], "Test completed")
        mem.close()

    def test_duplicate_is_idempotent(self):
        mem = EvidenceMemory(self.path, simulation=True)
        payload = ("e1", "t1", "ACS-02", "mock-run-1", "Test completed")
        self.assertEqual(mem.remember(*payload), "recorded")
        self.assertEqual(mem.remember(*payload), "duplicate")
        self.assertEqual(len(mem.for_task("t1")), 1)
        mem.close()

    def test_conflicting_evidence_cannot_overwrite(self):
        mem = EvidenceMemory(self.path, simulation=True)
        mem.remember("e1", "t1", "ACS-02", "mock-run-1", "one")
        with self.assertRaises(ProtocolError):
            mem.remember("e1", "t1", "ACS-02", "mock-run-2", "two")
        self.assertEqual(mem.for_task("t1")[0]["finding"], "one")
        mem.close()

    def test_task_records_are_isolated(self):
        mem = EvidenceMemory(self.path, simulation=True)
        mem.remember("e1", "t1", "ACS-02", "mock-run-1", "one")
        mem.remember("e2", "t2", "ACS-03", "mock-run-2", "two")
        self.assertEqual([x["evidence_id"] for x in mem.for_task("t1")], ["e1"])
        mem.close()

    def test_bad_ids_and_unknown_agents_rejected(self):
        mem = EvidenceMemory(self.path, simulation=True)
        for args in [
            ("bad space", "t1", "ACS-02", "mock-run", "ok"),
            ("e1", "t1", "unknown", "mock-run", "ok"),
            ("e1", "t1", "ACS-02", "bad/source", "ok"),
            ("e1", "t1", "ACS-02", "mock-run", ""),
        ]:
            with self.assertRaises(ProtocolError):
                mem.remember(*args)
        mem.close()

    def test_corrupted_database_not_silently_recreated(self):
        with open(self.path, "wb") as stream:
            stream.write(b"invalid-sqlite")
        with self.assertRaises(Exception):
            EvidenceMemory(self.path, simulation=True)


if __name__ == "__main__":
    unittest.main()
