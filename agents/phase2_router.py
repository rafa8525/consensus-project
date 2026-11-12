"""Simulation-only multi-agent task routing. No production integrations."""
from datetime import datetime, timezone
from uuid import uuid4

from agents.phase2_protocol import InMemoryExchange, ProtocolError, AGENTS, VERSION


class SimulatedRouter:
    """Explicitly injected mock handlers; no network, persistence, or scheduler."""

    def __init__(self, handlers, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        if not isinstance(handlers, dict) or not handlers:
            raise ProtocolError("mock handlers required")
        if any(name not in AGENTS or name == "planner" or not callable(fn)
               for name, fn in handlers.items()):
            raise ProtocolError("invalid mock handler registry")
        self.handlers = handlers.copy()
        self.exchange = InMemoryExchange()
        self._cache = {}

    @staticmethod
    def _message(task_id, correlation, kind, sender, recipient, status, payload,
                 evidence=None, attempt=1, max_attempts=2):
        return {
            "version": VERSION, "message_id": uuid4().hex, "task_id": task_id,
            "correlation_id": correlation, "idempotency_key": uuid4().hex,
            "sender": sender, "recipient": recipient, "kind": kind, "status": status,
            "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "attempt": attempt, "payload": payload, "evidence": evidence or [],
            "retry_policy": {"max_attempts": max_attempts, "backoff_seconds": 0},
        }

    def dispatch(self, task_id, worker, task, *, max_attempts=2):
        """Run one mock task with bounded retries and one acknowledgement."""
        if task_id in self._cache:
            old_worker, old_task, report = self._cache[task_id]
            if (old_worker, old_task) != (worker, task):
                raise ProtocolError("task ID collision with different assignment")
            return dict(report, duplicate=True)
        if not isinstance(task_id, str) or not task_id.strip() or len(task_id) > 128:
            raise ProtocolError("invalid task ID")
        if worker not in self.handlers:
            raise ProtocolError("worker not registered")
        if not isinstance(task, str) or not task.strip() or len(task) > 300:
            raise ProtocolError("invalid task")
        if type(max_attempts) is not int or not 1 <= max_attempts <= 3:
            raise ProtocolError("invalid retry count")
        correlation = uuid4().hex
        self.exchange.submit(self._message(task_id, correlation, "assignment", "planner",
                                           worker, "pending", {"task": task},
                                           max_attempts=max_attempts))
        errors = []
        for attempt in range(1, max_attempts + 1):
            try:
                output = self.handlers[worker](task)
                if not isinstance(output, str) or not output.strip():
                    raise ProtocolError("mock handler must return nonblank text")
                status, summary = "completed", output
                break
            except Exception as exc:
                errors.append(type(exc).__name__)
                if attempt == max_attempts:
                    status, summary = "failed", "mock handler exhausted retry budget"
        self.exchange.submit(self._message(task_id, correlation, "result", worker,
                                           "planner", status, {"summary": summary},
                                           ["mock-handler-only"], attempt=attempt,
                                           max_attempts=max_attempts))
        self.exchange.submit(self._message(task_id, correlation, "ack", "planner",
                                           worker, "accepted", {"accepted": True},
                                           max_attempts=max_attempts))
        report = {"task_id": task_id, "worker": worker, "execution_status": status,
                  "ack_status": self.exchange.status(task_id), "attempts": attempt,
                  "errors": tuple(errors), "mode": "simulation-only", "duplicate": False}
        self._cache[task_id] = (worker, task, report)
        return dict(report)
