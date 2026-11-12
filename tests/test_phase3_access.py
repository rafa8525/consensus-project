"""Mock-only identity and task permission tests."""
import os
import tempfile
import unittest
from agents.phase3_secure_memory import AuthorizedEvidenceMemory
from agents.phase2_protocol import ProtocolError


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, "memory.sqlite")
        self.grants = {"task1": {"ACS-02": {"read", "write"}, "planner": {"read"}},
                       "task2": {"ACS-03": {"read", "write"}}}

    def tearDown(self):
        self.temp.cleanup()

    def test_requires_simulation(self):
        with self.assertRaises(ProtocolError):
            AuthorizedEvidenceMemory(self.path, self.grants)

    def test_allowed_writer_and_reader(self):
        store = AuthorizedEvidenceMemory(self.path, self.grants, simulation=True)
        self.assertEqual(store.remember("ACS-02", "ev1", "task1", "ACS-02", "mock1", "synthetic"), "recorded")
        self.assertEqual(store.for_task("planner", "task1")[0]["finding"], "synthetic")
        store.close()

    def test_no_cross_task_leakage(self):
        store = AuthorizedEvidenceMemory(self.path, self.grants, simulation=True)
        store.remember("ACS-02", "ev1", "task1", "ACS-02", "mock1", "synthetic")
        for principal, task_id in (("ACS-03", "task1"), ("ACS-02", "task2"),
                                   ("executor", "task1"), ("unknown", "task1")):
            with self.assertRaises(ProtocolError):
                store.for_task(principal, task_id)
        store.close()

    def test_read_only_cannot_write(self):
        store = AuthorizedEvidenceMemory(self.path, self.grants, simulation=True)
        with self.assertRaises(ProtocolError):
            store.remember("planner", "ev1", "task1", "planner", "mock1", "synthetic")
        store.close()

    def test_spoofed_attribution_rejected(self):
        store = AuthorizedEvidenceMemory(self.path, self.grants, simulation=True)
        with self.assertRaises(ProtocolError):
            store.remember("ACS-02", "ev1", "task1", "ACS-03", "mock1", "synthetic")
        store.close()

    def test_default_deny(self):
        store = AuthorizedEvidenceMemory(self.path, {}, simulation=True)
        with self.assertRaises(ProtocolError):
            store.for_task("planner", "task1")
        store.close()

    def test_bad_grants_rejected(self):
        for grants in ({"t": {"unknown": {"read"}}}, {"t": {"planner": {"delete"}}},
                       {"t": {"planner": "read"}}):
            with self.assertRaises(ProtocolError):
                AuthorizedEvidenceMemory(self.path, grants, simulation=True)


if __name__ == "__main__":
    unittest.main()
