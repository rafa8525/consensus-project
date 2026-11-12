"""Phase 3 isolated, provenance-aware memory ledger (simulation only).

No network, external agent execution, credential handling, or production paths.
SQLite persistence is used solely for local tests and mock data.
"""
import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from agents.phase2_protocol import ProtocolError

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class EvidenceMemory:
    def __init__(self, path, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True is required")
        if not isinstance(path, (str, Path)) or str(path) in ("", ":memory:"):
            raise ProtocolError("a durable isolated database path is required")
        self.conn = sqlite3.connect(str(path), isolation_level=None, timeout=10)
        self.conn.execute("PRAGMA busy_timeout=10000")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS observations (
            evidence_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            source_ref TEXT NOT NULL,
            finding TEXT NOT NULL,
            finding_hash TEXT NOT NULL,
            observed_at TEXT NOT NULL
        )""")
        self.conn.execute("CREATE INDEX IF NOT EXISTS obs_task ON observations(task_id)")

    def close(self):
        self.conn.close()

    def remember(self, evidence_id, task_id, agent_id, source_ref, finding):
        for label, value in (("evidence_id", evidence_id), ("task_id", task_id),
                             ("agent_id", agent_id), ("source_ref", source_ref)):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise ProtocolError("invalid " + label)
        if agent_id not in {"planner", "executor", "ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05"}:
            raise ProtocolError("unauthorized agent")
        # The prototype deliberately accepts only short, synthetic statements.
        if not isinstance(finding, str) or not finding.strip() or len(finding) > 500:
            raise ProtocolError("invalid synthetic finding")
        digest = hashlib.sha256(finding.encode("utf-8")).hexdigest()
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            existing = self.conn.execute(
                "SELECT task_id,agent_id,source_ref,finding_hash FROM observations WHERE evidence_id=?",
                (evidence_id,)).fetchone()
            if existing:
                if existing != (task_id, agent_id, source_ref, digest):
                    raise ProtocolError("evidence id reused for different observation")
                result = "duplicate"
            else:
                self.conn.execute(
                    "INSERT INTO observations VALUES(?,?,?,?,?,?,?)",
                    (evidence_id, task_id, agent_id, source_ref,
                     finding, digest, _timestamp()))
                result = "recorded"
            self.conn.execute("COMMIT")
            return result
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise

    def for_task(self, task_id, *, limit=25):
        if not isinstance(task_id, str) or not _ID.fullmatch(task_id):
            raise ProtocolError("invalid task id")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ProtocolError("invalid limit")
        rows = self.conn.execute(
            "SELECT evidence_id,agent_id,source_ref,finding,observed_at "
            "FROM observations WHERE task_id=? ORDER BY evidence_id LIMIT ?",
            (task_id, limit)).fetchall()
        return [dict(zip(("evidence_id", "agent_id", "source_ref",
                          "finding", "observed_at"), row)) for row in rows]
