"""SQLite-backed, simulation-only task journal with fail-closed crash recovery.

Designed to verify restart behaviour BEFORE production integration. A task marked
running at interruption is uncertain: it will never be automatically re-executed.
"""
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from agents.phase2_protocol import AGENTS, ProtocolError

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DurableTaskJournal:
    def __init__(self, path, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        if not isinstance(path, (str, Path)) or str(path) in ("", ":memory:"):
            raise ProtocolError("durable file path required")
        self.path = str(path)
        self.db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=10000")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY, worker TEXT NOT NULL, task TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN
                ('pending','running','completed','failed','uncertain')),
            result TEXT, updated_at TEXT NOT NULL)""")

    def close(self):
        self.db.close()

    def _tx(self, action):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            result = action()
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def get(self, task_id):
        row = self.db.execute(
            "SELECT worker,task,state,result,updated_at FROM tasks WHERE task_id=?",
            (task_id,)).fetchone()
        if row is None:
            return None
        return dict(zip(("worker", "task", "state", "result", "updated_at"), row))

    def register(self, task_id, worker, task):
        if not isinstance(task_id, str) or not _ID.fullmatch(task_id):
            raise ProtocolError("invalid task id")
        if worker not in AGENTS or worker == "planner":
            raise ProtocolError("invalid worker")
        if not isinstance(task, str) or not task.strip() or len(task) > 300:
            raise ProtocolError("invalid task")
        def write():
            existing = self.get(task_id)
            if existing:
                if (existing["worker"], existing["task"]) != (worker, task):
                    raise ProtocolError("task id collision")
                return "duplicate"
            self.db.execute(
                "INSERT INTO tasks(task_id,worker,task,state,updated_at) VALUES(?,?,?,?,?)",
                (task_id, worker, task, "pending", _utc()))
            return "registered"
        return self._tx(write)

    def claim(self, task_id):
        def write():
            row = self.get(task_id)
            if row is None or row["state"] != "pending":
                raise ProtocolError("task not eligible for execution")
            self.db.execute(
                "UPDATE tasks SET state='running',updated_at=? WHERE task_id=? AND state='pending'",
                (_utc(), task_id))
            return "running"
        return self._tx(write)

    def finish(self, task_id, result, *, success):
        if type(success) is not bool or not isinstance(result, str) or not result.strip():
            raise ProtocolError("invalid execution result")
        def write():
            row = self.get(task_id)
            if row is None or row["state"] != "running":
                raise ProtocolError("task not running")
            state = "completed" if success else "failed"
            self.db.execute(
                "UPDATE tasks SET state=?,result=?,updated_at=? WHERE task_id=?",
                (state, result, _utc(), task_id))
            return state
        return self._tx(write)

    def recover_interrupted(self):
        """Fail closed: any running task may already have had external effects."""
        def write():
            cursor = self.db.execute(
                "UPDATE tasks SET state='uncertain',updated_at=? WHERE state='running'",
                (_utc(),))
            return cursor.rowcount
        return self._tx(write)


class DurableSimulatedRouter:
    """Only injected mock handlers; replay never executes a terminal/uncertain task."""

    def __init__(self, path, handlers, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        if not isinstance(handlers, dict) or not handlers or any(
            agent not in AGENTS or agent == "planner" or not callable(handler)
            for agent, handler in handlers.items()
        ):
            raise ProtocolError("mock handler registry required")
        self.handlers = dict(handlers)
        self.journal = DurableTaskJournal(path, simulation=True)
        # This occurs once on each new process/router instance, before new work.
        self.journal.recover_interrupted()

    def dispatch(self, task_id, worker, task):
        if worker not in self.handlers:
            raise ProtocolError("unregistered worker")
        registration = self.journal.register(task_id, worker, task)
        if registration == "duplicate":
            state = self.journal.get(task_id)["state"]
            return {"task_id": task_id, "state": state, "replayed": True,
                    "executed": False}
        self.journal.claim(task_id)
        try:
            output = self.handlers[worker](task)
            if not isinstance(output, str) or not output.strip():
                raise ProtocolError("mock handler returned malformed result")
        except Exception:
            # Side effects might have happened; record failure but never retry here.
            self.journal.finish(task_id, "mock-execution-failed", success=False)
            return {"task_id": task_id, "state": "failed", "replayed": False,
                    "executed": True}
        self.journal.finish(task_id, output, success=True)
        return {"task_id": task_id, "state": "completed", "replayed": False,
                "executed": True}

    def close(self):
        self.journal.close()
