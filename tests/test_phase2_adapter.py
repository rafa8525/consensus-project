"""Phase 2 opt-in integration with existing prototype Planner and Executor."""
import unittest
from unittest.mock import patch

from agents.phase2_adapter import simulate_handshake
from agents.phase2_protocol import ProtocolError


class Phase2AdapterTests(unittest.TestCase):
    def test_guard_rejects_default_and_non_boolean(self):
        with self.assertRaises(ProtocolError):
            simulate_handshake("safe goal")
        with self.assertRaises(ProtocolError):
            simulate_handshake("safe goal", simulation=1)

    def test_invalid_goal_fails_closed(self):
        for goal in ("", " ", 123, "x" * 301):
            with self.subTest(goal=str(goal)[:12]):
                with self.assertRaises(ProtocolError):
                    simulate_handshake(goal, simulation=True)

    @patch("agents.executor.time.sleep", return_value=None)
    def test_real_planner_executor_success_handshake(self, _sleep):
        report = simulate_handshake("review research", simulation=True)
        self.assertEqual(report["mode"], "simulation-only")
        self.assertEqual(report["execution_status"], "completed")
        self.assertEqual(report["ack_status"], "accepted")
        self.assertEqual(report["message_count"], 3)

    @patch("agents.executor.time.sleep", return_value=None)
    def test_real_planner_executor_failure_handshake(self, _sleep):
        report = simulate_handshake("simulate error", simulation=True)
        self.assertEqual(report["execution_status"], "failed")
        self.assertEqual(report["ack_status"], "accepted")

    @patch("agents.phase2_adapter.Executor")
    def test_malformed_executor_output_fails_closed(self, mock_executor):
        mock_executor.return_value.execute.return_value = ["unknown"]
        with self.assertRaises(ProtocolError):
            simulate_handshake("safe goal", simulation=True)


if __name__ == "__main__":
    unittest.main()
