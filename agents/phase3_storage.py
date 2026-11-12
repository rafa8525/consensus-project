"""Phase 3 simulated durable authorization and SQLite backup utilities.

Prototype policy enforcement only: caller identities are assertions, not verified
credentials, and direct DB access bypasses this facade. Do not use with personal data.
"""
import hashlib
import os
import re
import sqlite3
from pathlib import Path

from agents.phase2_protocol import ProtocolError
from agents.phase3_memory import EvidenceMemory

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_AGENTS = frozenset(("planner", "executor", "ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05"))
_PERMS = frozenset(("read", "write"))


class DurableAuthorizedMemory:
    """File-persistent ACLs checked for each mock read and write."""

    def __init__(self, path, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("explicit simulation=True required")
        self.memory = EvidenceMemory(path, simulation=True)
        try:
            self.memory.conn.execute("""CREATE TABLE IF NOT EXISTS grants (
                task_id TEXT NOT NULL, principal TEXT NOT NULL,
                permission TEXT NOT NULL CHECK(permission IN ('read','write')),
                PRIMARY KEY (task_id, principal, permission)
            )""")
        except BaseException:
            self.memory.close()
            raise

    def _validate(self, task_id, principal, permission):
        if not isinstance(task_id, str) or not _ID.fullmatch(task_id):
            raise ProtocolError("invalid task ID")
        if principal not in _AGENTS or permission not in _PERMS:
            raise ProtocolError("invalid principal or permission")

    def grant(self, task_id, principal, permission, *, bootstrap=False):
        """Only explicit test bootstrap can create a grant. No implicit escalation."""
        self._validate(task_id, principal, permission)
        if bootstrap is not True:
            raise ProtocolError("bootstrap authorization required")
        self.memory.conn.execute(
            "INSERT OR IGNORE INTO grants(task_id,principal,permission) VALUES(?,?,?)",
            (task_id, principal, permission))

    def revoke(self, task_id, principal, permission, *, bootstrap=False):
        self._validate(task_id, principal, permission)
        if bootstrap is not True:
            raise ProtocolError("bootstrap authorization required")
        self.memory.conn.execute(
            "DELETE FROM grants WHERE task_id=? AND principal=? AND permission=?",
            (task_id, principal, permission))

    def _authorize(self, task_id, principal, permission):
        self._validate(task_id, principal, permission)
        row = self.memory.conn.execute(
            "SELECT 1 FROM grants WHERE task_id=? AND principal=? AND permission=?",
            (task_id, principal, permission)).fetchone()
        if row is None:
            raise ProtocolError("access denied")

    def remember(self, principal, evidence_id, task_id, source_ref, finding):
        self._authorize(task_id, principal, "write")
        return self.memory.remember(evidence_id, task_id, principal, source_ref, finding)

    def for_task(self, principal, task_id, *, limit=25):
        self._authorize(task_id, principal, "read")
        return self.memory.for_task(task_id, limit=limit)

    def close(self):
        self.memory.close()


def backup_sqlite(source, destination, *, simulation=False):
    """Create verified SQLite snapshot with the native backup API, never raw WAL copy."""
    if simulation is not True:
        raise ProtocolError("simulation=True required")
    if not isinstance(source, (str, Path)) or not isinstance(destination, (str, Path)):
        raise ProtocolError("file paths required")
    source, destination = Path(source), Path(destination)
    if not source.is_file() or destination.exists() or source.resolve() == destination.resolve():
        raise ProtocolError("source must exist and destination must be new")
    if source.is_symlink() or destination.is_symlink():
        raise ProtocolError("symlink paths disallowed")
    target = None
    original = None
    try:
        original = sqlite3.connect("file:" + str(source.resolve()) + "?mode=ro", uri=True, timeout=10)
        if original.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ProtocolError("source database integrity failure")
        target = sqlite3.connect(str(destination), timeout=10)
        original.backup(target)
        target.commit()
        if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ProtocolError("backup integrity failure")
        # Hash is a local consistency fingerprint, not independent trusted evidence.
        target.close()
        target = None
        data = destination.read_bytes()
        return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                "integrity": "ok", "evidence": "local-simulation-only"}
    except BaseException:
        if target is not None:
            target.close()
        if destination.exists():
            destination.unlink()
        raise
    finally:
        if original is not None:
            original.close()


def restore_sqlite(snapshot, destination, *, simulation=False, expected_sha256=None):
    """Restore only to a new sandbox file; validate snapshot hash and SQLite integrity."""
    if simulation is not True:
        raise ProtocolError("simulation=True required")
    if not isinstance(snapshot, (str, Path)) or not isinstance(destination, (str, Path)):
        raise ProtocolError("file paths required")
    snapshot, destination = Path(snapshot), Path(destination)
    if not snapshot.is_file() or destination.exists() or snapshot.is_symlink() or destination.is_symlink():
        raise ProtocolError("invalid restore source or target")
    data = snapshot.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if not isinstance(expected_sha256, str) or digest != expected_sha256:
        raise ProtocolError("snapshot checksum mismatch")
    source = None
    target = None
    try:
        source = sqlite3.connect("file:" + str(snapshot.resolve()) + "?mode=ro", uri=True, timeout=10)
        if source.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ProtocolError("snapshot integrity failure")
        target = sqlite3.connect(str(destination), timeout=10)
        source.backup(target)
        target.commit()
        if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ProtocolError("restored database integrity failure")
        return {"restored": True, "evidence": "local-simulation-only"}
    except BaseException:
        if target is not None:
            target.close()
            target = None
        if destination.exists():
            destination.unlink()
        raise
    finally:
        if target is not None:
            target.close()
        if source is not None:
            source.close()
