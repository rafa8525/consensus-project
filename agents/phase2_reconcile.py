"""Fail-closed reconciliation of uncertain simulated tasks.

Evidence is supplied by an injected, side-effect-free mock verifier. Nothing
here retries the work or calls a production integration.
"""
from agents.phase2_protocol import ProtocolError


class UncertainTaskReconciler:
    def __init__(self, journal, verifiers, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("explicit simulation=True required")
        if not isinstance(verifiers, dict) or not verifiers or any(
            not isinstance(name, str) or not callable(verify)
            for name, verify in verifiers.items()
        ):
            raise ProtocolError("mock verifier registry required")
        self.journal = journal
        self.verifiers = dict(verifiers)

    def reconcile(self, task_id):
        row = self.journal.get(task_id)
        if row is None or row["state"] != "uncertain":
            raise ProtocolError("only uncertain tasks can be reconciled")
        verifier = self.verifiers.get(row["worker"])
        if verifier is None:
            return {"task_id": task_id, "state": "uncertain", "reason": "no_verifier"}
        try:
            evidence = verifier(task_id, row["task"])
        except Exception:
            return {"task_id": task_id, "state": "uncertain", "reason": "verifier_error"}
        # Require explicit task binding, deterministic mock proof and known result.
        if not isinstance(evidence, dict) or set(evidence) != {
            "task_id", "outcome", "proof_id"
        } or evidence["task_id"] != task_id or evidence["outcome"] not in {
            "completed", "failed"
        } or not isinstance(evidence["proof_id"], str) or not evidence["proof_id"].strip():
            return {"task_id": task_id, "state": "uncertain", "reason": "insufficient_evidence"}
        # Prevent untrusted text from becoming arbitrary task result data.
        proof = evidence["proof_id"]
        if len(proof) > 128 or not all(c.isalnum() or c in "._:-" for c in proof):
            return {"task_id": task_id, "state": "uncertain", "reason": "insufficient_evidence"}
        outcome = evidence["outcome"]
        def write():
            current = self.journal.get(task_id)
            if current is None or current["state"] != "uncertain":
                raise ProtocolError("reconciliation race or invalid state")
            cursor = self.journal.db.execute(
                "UPDATE tasks SET state=?, result=?, updated_at=? "
                "WHERE task_id=? AND state='uncertain'",
                (outcome, "mock-verified:" + proof, self._utc(), task_id))
            if cursor.rowcount != 1:
                raise ProtocolError("concurrent reconciliation")
            return outcome
        resolved = self.journal._tx(write)
        return {"task_id": task_id, "state": resolved, "reason": "mock_verified", "proof_id": proof}

    @staticmethod
    def _utc():
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
