"""Simulated multi-agent routing and negative-case regression tests."""
import unittest
from agents.phase2_protocol import ProtocolError
from agents.phase2_router import SimulatedRouter


class RouterTests(unittest.TestCase):
    def test_explicit_simulation_required(self):
        with self.assertRaises(ProtocolError):
            SimulatedRouter({"executor": lambda task: "ok"})

    def test_two_mock_agents(self):
        bus = SimulatedRouter({"executor": lambda task: "done",
                               "ACS-02": lambda task: "knowledge done"}, simulation=True)
        a = bus.dispatch("one", "executor", "task")
        b = bus.dispatch("two", "ACS-02", "other task")
        self.assertEqual((a["execution_status"], b["execution_status"]), ("completed", "completed"))
        self.assertEqual((a["ack_status"], b["ack_status"]), ("accepted", "accepted"))

    def test_duplicate_no_reexecution(self):
        calls = []
        bus = SimulatedRouter({"executor": lambda task: calls.append(task) or "ok"}, simulation=True)
        bus.dispatch("one", "executor", "task")
        duplicate = bus.dispatch("one", "executor", "task")
        self.assertEqual(calls, ["task"])
        self.assertTrue(duplicate["duplicate"])

    def test_task_id_collision(self):
        bus = SimulatedRouter({"executor": lambda task: "ok"}, simulation=True)
        bus.dispatch("one", "executor", "task")
        with self.assertRaises(ProtocolError):
            bus.dispatch("one", "executor", "changed")

    def test_transient_failure_recovers(self):
        calls = []
        def flaky(task):
            calls.append(task)
            if len(calls) == 1:
                raise TimeoutError("simulated")
            return "recovered"
        bus = SimulatedRouter({"executor": flaky}, simulation=True)
        report = bus.dispatch("one", "executor", "task")
        self.assertEqual(report["execution_status"], "completed")
        self.assertEqual(report["attempts"], 2)
        self.assertEqual(report["errors"], ("TimeoutError",))

    def test_permanent_failure_is_bounded(self):
        calls = []
        def broken(task):
            calls.append(task)
            raise RuntimeError("private data")
        bus = SimulatedRouter({"executor": broken}, simulation=True)
        report = bus.dispatch("one", "executor", "task", max_attempts=3)
        self.assertEqual(report["execution_status"], "failed")
        self.assertEqual(report["ack_status"], "accepted")
        self.assertEqual(len(calls), 3)
        self.assertNotIn("private data", str(report))

    def test_unregistered_worker(self):
        bus = SimulatedRouter({"executor": lambda task: "ok"}, simulation=True)
        with self.assertRaises(ProtocolError):
            bus.dispatch("one", "ACS-05", "task")

    def test_invalid_retry_bounds(self):
        bus = SimulatedRouter({"executor": lambda task: "ok"}, simulation=True)
        for n in (0, 4, True):
            with self.assertRaises(ProtocolError):
                bus.dispatch("one", "executor", "task", max_attempts=n)

    def test_malformed_result_fails_closed(self):
        bus = SimulatedRouter({"executor": lambda task: None}, simulation=True)
        report = bus.dispatch("one", "executor", "task", max_attempts=1)
        self.assertEqual(report["execution_status"], "failed")
        self.assertEqual(report["errors"], ("ProtocolError",))


if __name__ == "__main__":
    unittest.main()
