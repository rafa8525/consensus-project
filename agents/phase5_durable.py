"""Durable, fail-closed mock integration delivery journal.

Uses SQLite atomic claims before mock handler execution. After a crash, a
claimed task is held as uncertain; no automatic replay. No real integrations.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from agents.phase2_protocol import ProtocolError
from agents.phase5_registry import MockIntegrationRegistry, _identifier

class DurableMockRegistry(MockIntegrationRegistry):
    def __init__(self, path, *, simulation=False):
        super().__init__(simulation=simulation)
        if not isinstance(path, (str, Path)) or str(path) in ("", ":memory:"):
            raise ProtocolError("durable path required")
        self.db = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        try:
            self.db.execute("PRAGMA busy_timeout=10000")
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("""CREATE TABLE IF NOT EXISTS deliveries(
                adapter_id TEXT NOT NULL, event_id TEXT NOT NULL,
                fingerprint TEXT NOT NULL, state TEXT NOT NULL,
                result TEXT, PRIMARY KEY(adapter_id,event_id))""")
            # No blanket recovery SQL necessary: 'claimed' always blocks replay.
        except BaseException:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def dispatch(self, *, adapter_id, principal, permission, event_id, payload):
        # Validate before claiming; no permission bypass on replay.
        if not _identifier(event_id) or not _identifier(principal):
            raise ProtocolError("invalid caller or event")
        adapter = self._adapters.get(adapter_id)
        if adapter is None or principal != adapter["owner"] or permission not in adapter["permissions"]:
            raise ProtocolError("access denied")
        if not isinstance(payload, dict) or set(payload) != {"synthetic_value"}:
            raise ProtocolError("synthetic payload required")
        v = payload["synthetic_value"]
        if type(v) not in (str, int, float, bool) or (type(v) is str and len(v) > 120):
            raise ProtocolError("invalid synthetic value")
        # Include authorization in fingerprint to reject conflicting replays.
        digest = hashlib.sha256(json.dumps(
            [adapter_id,principal,permission,payload],sort_keys=True,separators=(",",":")
        ).encode()).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute(
                "SELECT fingerprint,state,result FROM deliveries WHERE adapter_id=? AND event_id=?",
                (adapter_id,event_id)).fetchone()
            if previous:
                if previous[0] != digest:
                    raise ProtocolError("event collision")
                self.db.execute("COMMIT")
                return {"adapter_id":adapter_id,"status":previous[1],
                        "duplicate":True,"executed":False}
            self.db.execute(
                "INSERT INTO deliveries VALUES(?,?,?,?,?)",
                (adapter_id,event_id,digest,"claimed",None))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        # Intent is durably claimed *before* handler; crash -> claimed (uncertain).
        try:
            output = adapter["handler"](dict(payload))
            if not isinstance(output,str) or not output.strip() or len(output)>160:
                raise ProtocolError("invalid mock output")
            state = "delivered"
        except Exception:
            state,output = "uncertain",None
        self.db.execute(
            "UPDATE deliveries SET state=?,result=? WHERE adapter_id=? AND event_id=? AND state='claimed'",
            (state,output,adapter_id,event_id))
        return {"adapter_id":adapter_id,"status":state,"duplicate":False,"executed":True}
