"""Delivery reconciliation: mock receipts, collisions, no replay."""
import os
import tempfile
import unittest
from agents.phase2_protocol import ProtocolError
from agents.phase5_durable import DurableMockRegistry
from agents.phase5_reconcile import MockDeliveryReconciler


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "mock-events.sqlite")
        self.calls = []
        self.reg = DurableMockRegistry(self.path, simulation=True)
        self.reg.register(adapter_id="alerts.mock", capability="notifications",
                          workflow_key="existing.alerts", owner="acs-02",
                          permissions={"notify_mock"},
                          handler=lambda p: self.calls.append(p) or "ok")
        self.event_id = "event1"
        self.reg.db.execute(
            "INSERT INTO deliveries(adapter_id,event_id,fingerprint,state,result) "
            "VALUES('alerts.mock','event1',?,'claimed',NULL)", ("a" * 64,))
    def tearDown(self):
        self.reg.close()
        self.tmp.cleanup()
    def verifier(self, outcome="delivered", event_id="event1", fingerprint=None):
        return lambda adapter, event, digest: {
            "adapter_id": adapter, "event_id": event_id,
            "fingerprint": fingerprint or digest, "outcome": outcome,
            "proof_id": "mock-receipt-42"}
    def reconciler(self, fn):
        return MockDeliveryReconciler(
            self.reg, {"alerts.mock": fn}, simulation=True)
    def test_receipt_closes_without_execution(self):
        rec = self.reconciler(self.verifier())
        r = rec.reconcile("alerts.mock", self.event_id)
        self.assertEqual(r["state"], "delivered")
        self.assertEqual(self.calls, [])
        self.assertEqual(rec.reconcile("alerts.mock", self.event_id)["reason"], "already_final")
    def test_negative_receipt_needs_review_not_retry(self):
        rec = self.reconciler(self.verifier(outcome="not_delivered"))
        self.assertEqual(rec.reconcile("alerts.mock", self.event_id)["state"], "needs_review")
        self.assertEqual(self.calls, [])
    def test_bad_or_unbound_receipt_leaves_claimed(self):
        for fn in (self.verifier(event_id="other"),
                   self.verifier(fingerprint="b" * 64),
                   lambda *a: None,
                   lambda *a: {"outcome": "delivered"}):
            result = self.reconciler(fn).reconcile("alerts.mock", self.event_id)
            self.assertEqual(result["state"], "claimed")
            self.assertFalse(result["reconciled"])
    def test_verifier_exception_redacted(self):
        def fail(*args):
            raise RuntimeError("secret-token")
        r = self.reconciler(fail).reconcile("alerts.mock", self.event_id)
        self.assertEqual(r["reason"], "verifier_error")
        self.assertNotIn("secret-token", str(r))
    def test_unauthorized_reconciliation_disabled(self):
        with self.assertRaises(ProtocolError):
            MockDeliveryReconciler(self.reg, {"alerts.mock": self.verifier()})
    def test_unknown_event_rejected(self):
        with self.assertRaises(ProtocolError):
            self.reconciler(self.verifier()).reconcile("alerts.mock", "missing")
    def test_conflicting_state_change_rejected(self):
        def racing(a, e, digest):
            self.reg.db.execute("UPDATE deliveries SET state='delivered' WHERE event_id=?", (e,))
            return {"adapter_id": a, "event_id": e, "fingerprint": digest,
                    "outcome": "delivered", "proof_id": "proof"}
        with self.assertRaises(ProtocolError):
            self.reconciler(racing).reconcile("alerts.mock", self.event_id)


if __name__ == "__main__":
    unittest.main()
