"""Phase 2 isolated Planner -> Executor handshake.

This module is opt-in and deliberately has no production integration. The legacy
Planner/Executor are invoked only in local simulation, with no scheduler or APIs.
"""
from datetime import datetime, timezone
from uuid import uuid4

from agents.planner import Planner
from agents.executor import Executor
from agents.phase2_protocol import InMemoryExchange, ProtocolError, VERSION


def _envelope(task_id, correlation_id, kind, sender, recipient, status, payload,
              evidence=None):
    return {
        "version": VERSION,
        "message_id": uuid4().hex,
        "task_id": task_id,
        "correlation_id": correlation_id,
        "idempotency_key": uuid4().hex,
        "sender": sender,
        "recipient": recipient,
        "kind": kind,
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "attempt": 1,
        "payload": payload,
        "evidence": evidence or [],
        "retry_policy": {"max_attempts": 1, "backoff_seconds": 0},
    }


def simulate_handshake(goal, *, simulation=False):
    """Run one bounded legacy Planner/Executor task with in-memory messages only.

    Explicit simulation=True is mandatory. This does not publish, schedule,
    persist, make network calls, or modify production agent configuration.
    """
    if simulation is not True:
        raise ProtocolError("explicit simulation=True required")
    if not isinstance(goal, str) or not goal.strip() or len(goal) > 300:
        raise ProtocolError("goal must be 1-300 nonblank characters")
    tasks = Planner().plan(goal.strip())
    if not isinstance(tasks, list) or not tasks or not isinstance(tasks[0], str):
        raise ProtocolError("planner returned invalid tasks")
    task = tasks[0]
    task_id, correlation_id = uuid4().hex, uuid4().hex
    exchange = InMemoryExchange()
    assignment = _envelope(task_id, correlation_id, "assignment", "planner",
                           "executor", "pending", {"task": task})
    exchange.submit(assignment)
    # Deliberately bounded to one task, with the repo's existing mock-like
    # Executor. Its result strings are an existing prototype convention.
    output = Executor().execute([task])
    if not isinstance(output, list) or len(output) != 1 or not isinstance(output[0], str):
        raise ProtocolError("executor returned malformed result")
    success = output[0].startswith("✅")
    failure = output[0].startswith("❌")
    if not (success or failure):
        raise ProtocolError("executor result is not a recognized outcome")
    result = _envelope(task_id, correlation_id, "result", "executor",
                       "planner", "completed" if success else "failed",
                       {"summary": output[0]}, ["local-simulation-only"])
    exchange.submit(result)
    ack = _envelope(task_id, correlation_id, "ack", "planner", "executor",
                    "accepted", {"accepted": True})
    exchange.submit(ack)
    return {
        "mode": "simulation-only",
        "task_id": task_id,
        "task": task,
        "execution_status": result["status"],
        "ack_status": exchange.status(task_id),
        "message_count": 3,
        "evidence": ["local-simulation-only"],
    }
