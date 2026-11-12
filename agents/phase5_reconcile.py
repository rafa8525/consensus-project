"""Fail-closed reconciliation for durable synthetic integration deliveries.

A read-only mock receipt verifier must bind an observed event to its prior
SHA-256 fingerprint. No automatic replay is permitted and no claims of real
external delivery are made.
"""
import re
from agents.phase2_protocol import ProtocolError

PROOF = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$")


class MockDeliveryReconciler:
    def __init__(self, registry, verifiers, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        if not isinstance(verifiers, dict) or any(
            not isinstance(key, str) or not callable(fn)
            for key, fn in verifiers.items()
        ):
            raise ProtocolError("mock verifier registry required")
        self.registry = registry
        self.verifiers = dict(verifiers)

    def reconcile(self, adapter_id, event_id):
        row = self.registry.db.execute(
            "SELECT fingerprint,state FROM deliveries WHERE adapter_id=? AND event_id=?",
            (adapter_id, event_id)).fetchone()
        if row is None:
            raise ProtocolError("unknown event")
        fingerprint, state = row
        if state not in ("claimed", "uncertain"):
            return {"state": state, "reconciled": False, "reason": "already_final"}
        verifier = self.verifiers.get(adapter_id)
        if verifier is None:
            return {"state": state, "reconciled": False, "reason": "no_verifier"}
        try:
            receipt = verifier(adapter_id, event_id, fingerprint)
        except Exception:
            return {"state": state, "reconciled": False, "reason": "verifier_error"}
        if (not isinstance(receipt, dict) or set(receipt) !=
            {"adapter_id", "event_id", "fingerprint", "outcome", "proof_id"} or
            receipt["adapter_id"] != adapter_id or receipt["event_id"] != event_id or
            receipt["fingerprint"] != fingerprint or
            receipt["outcome"] not in ("delivered", "not_delivered") or
            not isinstance(receipt["proof_id"], str) or
            not PROOF.fullmatch(receipt["proof_id"])):
            return {"state": state, "reconciled": False, "reason": "insufficient_evidence"}
        # Observed 'not_delivered' is NOT a permit to replay: human review
        # is required even when the mock receipt is negative.
        resolved = "delivered" if receipt["outcome"] == "delivered" else "needs_review"
        self.registry.db.execute("BEGIN IMMEDIATE")
        try:
            changed = self.registry.db.execute(
                "UPDATE deliveries SET state=?,result=? "
                "WHERE adapter_id=? AND event_id=? AND fingerprint=? "
                "AND state IN ('claimed','uncertain')",
                (resolved, "mock-proof:" + receipt["proof_id"],
                 adapter_id, event_id, fingerprint))
            if changed.rowcount != 1:
                raise ProtocolError("concurrent reconciliation or changed event")
            self.registry.db.execute("COMMIT")
        except BaseException:
            self.registry.db.execute("ROLLBACK")
            raise
        return {"state": resolved, "reconciled": True, "reason": "mock_observed",
                "proof_id": receipt["proof_id"]}
