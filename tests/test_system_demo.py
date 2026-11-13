"""Phase 2-5 integration acceptance: deterministic mock workflow and restart."""
import os
import tempfile
import unittest
from datetime import datetime, timezone

from agents.phase2_protocol import ProtocolError
from agents.phase2_durable import DurableTaskJournal
from agents.phase3_pipeline import SimulatedEvidencePipeline
from agents.phase4_evaluator import EvaluationError
from agents.phase4_observation import evaluate_observed
from agents.phase5_durable import DurableMockRegistry
from agents.system_demo import run_mock_workflow, build_registry, _demo_measurements

NOW = datetime(2026, 11, 12, 22, 0, tzinfo=timezone.utc)


class SystemDemoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
    def tearDown(self):
        self.tmp.cleanup()

    def test_end_to_end_and_restart_have_no_duplicates(self):
        result = run_mock_workflow(self.tmp.name, now=NOW, simulation=True)
        self.assertEqual(result["task_first_status"], "completed")
        self.assertEqual(result["notification_first_status"], "delivered")
        self.assertFalse(result["task_replay_executed"])
        self.assertFalse(result["notification_replay_executed"])
        self.assertEqual(result["task_execution_count"], 1)
        self.assertEqual(result["notification_count"], 1)
        self.assertEqual(result["evidence_count_before"], 1)
        self.assertEqual(result["evidence_count_after"], 1)
        self.assertEqual(result["candidate_decision"], "ELIGIBLE_FOR_REVIEW")
        self.assertFalse(result["candidate_deployed"])

    def test_synthetic_end_to_end_never_contacts_external_services(self):
        # Block attempted network and child-process calls, not just returned values.
        # This test exercises the actual combined Phase 2-5 mock workflow.
        from unittest.mock import patch
        from socket import socket
        import subprocess
        import urllib.request

        def forbidden(*args, **kwargs):
            self.fail("isolated system demo attempted an external operation")

        with patch.object(socket, "connect", forbidden), \
             patch.object(socket, "connect_ex", forbidden), \
             patch.object(urllib.request, "urlopen", forbidden), \
             patch.object(subprocess, "Popen", forbidden):
            result = run_mock_workflow(self.tmp.name, now=NOW, simulation=True)
        self.assertEqual(result["mode"], "synthetic-isolated-demo")
        self.assertFalse(result["candidate_deployed"])
        self.assertEqual(result["task_execution_count"], 1)
        self.assertEqual(result["notification_count"], 1)

    def test_actual_interrupted_task_blocks_downstream_notification(self):
        path = os.path.join(self.tmp.name, "task.sqlite")
        journal = DurableTaskJournal(path, simulation=True)
        journal.register("task1", "executor", "synthetic")
        journal.claim("task1")
        journal.close()
        called = []
        p = SimulatedEvidencePipeline(
            path, os.path.join(self.tmp.name, "memory.sqlite"),
            {"executor": lambda task: called.append(task) or "done"}, simulation=True)
        report = p.dispatch("task1", "executor", "synthetic")
        self.assertEqual(report["state"], "uncertain")
        self.assertEqual(report["memory_status"], "not_recorded")
        self.assertEqual(called, [])
        p.close()

    def test_reject_spoofed_notification_identity(self):
        registry = build_registry(os.path.join(self.tmp.name, "events.sqlite"), [])
        try:
            with self.assertRaises(ProtocolError):
                registry.dispatch(
                    adapter_id="notifications.mock", principal="acs-03",
                    permission="notify_mock", event_id="event.demo1",
                    payload={"synthetic_value": "work done"})
        finally:
            registry.close()

    def test_observer_disagreement_blocks_promotion(self):
        fixture, observed = _demo_measurements(NOW)
        observed["candidate"]["metrics"]["latency_ms"] = 1.0
        with self.assertRaises(EvaluationError):
            evaluate_observed(fixture, observed, now=NOW, simulation=True)

    def test_simulation_required(self):
        with self.assertRaises(ProtocolError):
            run_mock_workflow(self.tmp.name, now=NOW)


if __name__ == "__main__":
    unittest.main()
