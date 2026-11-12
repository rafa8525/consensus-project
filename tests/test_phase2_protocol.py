"""Offline contract and negative tests. Run: python -m unittest discover -s tests -p 'test_phase2_protocol.py'."""
import copy
from datetime import datetime, timezone, timedelta
import unittest

from agents.phase2_protocol import InMemoryExchange, ProtocolError, validate

NOW = datetime(2026, 11, 12, 19, 0, tzinfo=timezone.utc)
STAMP = NOW.isoformat().replace("+00:00", "Z")


def envelope(kind="assignment", status="pending", message_id="m1", key="key1",
             sender="planner", recipient="executor", payload=None, stamp=STAMP):
    if payload is None:
        payload = {"task": "Review mocked agent input"} if kind == "assignment" else (
            {"summary": "Simulated execution completed"} if kind == "result" else {"accepted": True})
    return {
        "version": "1.0", "message_id": message_id, "task_id": "task1",
        "correlation_id": "corr1", "idempotency_key": key,
        "sender": sender, "recipient": recipient, "kind": kind, "status": status,
        "created_at_utc": stamp, "attempt": 1, "payload": payload,
        "evidence": ["mock-run-001"] if kind == "result" else [],
        "retry_policy": {"max_attempts": 3, "backoff_seconds": 10},
    }


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.bus = InMemoryExchange()
        self.assignment = envelope()

    def test_round_trip_and_ack(self):
        self.assertEqual(self.bus.submit(self.assignment, NOW), "accepted")
        self.assertEqual(self.bus.status("task1"), "pending")
        result = envelope("result", "completed", "m2", "key2", "executor", "planner")
        self.assertEqual(self.bus.submit(result, NOW), "accepted")
        ack = envelope("ack", "accepted", "m3", "key3", "planner", "executor")
        self.assertEqual(self.bus.submit(ack, NOW), "accepted")
        self.assertEqual(self.bus.status("task1"), "accepted")

    def test_failed_result_can_be_acknowledged(self):
        self.bus.submit(self.assignment, NOW)
        self.bus.submit(envelope("result", "failed", "m2", "key2", "executor", "planner"), NOW)
        self.bus.submit(envelope("ack", "accepted", "m3", "key3"), NOW)
        self.assertEqual(self.bus.status("task1"), "accepted")

    def test_duplicate_delivery_is_idempotent(self):
        self.bus.submit(self.assignment, NOW)
        self.assertEqual(self.bus.submit(copy.deepcopy(self.assignment), NOW), "duplicate")
        self.assertEqual(self.bus.status("task1"), "pending")

    def test_reused_message_id_with_changed_content_fails(self):
        self.bus.submit(self.assignment, NOW)
        altered = copy.deepcopy(self.assignment)
        altered["payload"]["task"] = "different"
        with self.assertRaises(ProtocolError):
            self.bus.submit(altered, NOW)

    def test_duplicate_key_for_other_task_fails(self):
        self.bus.submit(self.assignment, NOW)
        altered = envelope(message_id="m4")
        altered["task_id"] = "task2"
        with self.assertRaises(ProtocolError):
            self.bus.submit(altered, NOW)

    def test_result_before_assignment_rejected(self):
        with self.assertRaises(ProtocolError):
            self.bus.submit(envelope("result", "completed", "m2", "key2", "executor", "planner"), NOW)

    def test_ack_before_result_rejected(self):
        self.bus.submit(self.assignment, NOW)
        with self.assertRaises(ProtocolError):
            self.bus.submit(envelope("ack", "accepted", "m3", "key3"), NOW)

    def test_out_of_order_time_rejected(self):
        self.bus.submit(self.assignment, NOW)
        earlier = (NOW - timedelta(seconds=5)).isoformat().replace("+00:00", "Z")
        with self.assertRaises(ProtocolError):
            self.bus.submit(envelope("result", "completed", "m2", "key2", "executor", "planner", stamp=earlier), NOW)

    def test_stale_and_future_rejected(self):
        for offset in (-301, 31):
            m = envelope(stamp=(NOW + timedelta(seconds=offset)).isoformat().replace("+00:00", "Z"))
            with self.assertRaises(ProtocolError):
                validate(m, NOW)

    def test_malformed_missing_extra_fields(self):
        for changed in ({"version": "4.0"}, {"sender": "unknown"}, {"status": "completed"},
                        {"attempt": 0}, {"payload": {}}, {"evidence": "unverified"},
                        {"retry_policy": {"max_attempts": 0, "backoff_seconds": 10}}):
            m = copy.deepcopy(self.assignment)
            m.update(changed)
            with self.assertRaises(ProtocolError):
                validate(m, NOW)
        m = copy.deepcopy(self.assignment)
        del m["task_id"]
        with self.assertRaises(ProtocolError):
            validate(m, NOW)
        m = copy.deepcopy(self.assignment)
        m["extra"] = "unexpected"
        with self.assertRaises(ProtocolError):
            validate(m, NOW)

    def test_spoofed_result_rejected(self):
        self.bus.submit(self.assignment, NOW)
        with self.assertRaises(ProtocolError):
            self.bus.submit(envelope("result", "completed", "m2", "key2", "ACS-05", "planner"), NOW)

    def test_no_repeat_result_after_completion(self):
        self.bus.submit(self.assignment, NOW)
        self.bus.submit(envelope("result", "completed", "m2", "key2", "executor", "planner"), NOW)
        with self.assertRaises(ProtocolError):
            self.bus.submit(envelope("result", "completed", "m4", "key4", "executor", "planner"), NOW)


if __name__ == "__main__":
    unittest.main()
