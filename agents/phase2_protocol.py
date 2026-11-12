"""Isolated, standard-library Phase 2 task envelope and in-memory exchange.

No network, file, production executor, or scheduler side effects.
"""
from datetime import datetime, timezone
import copy
import re

VERSION = "1.0"
KINDS = {"assignment", "result", "ack"}
STATUSES = {"pending", "completed", "failed", "accepted"}
TRANSITIONS = {
    None: {"assignment": "pending"},
    "pending": {"result": {"completed", "failed"}},
    "completed": {"ack": "accepted"},
    "failed": {"ack": "accepted"},
}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
AGENTS = {"ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05", "planner", "executor"}
REQUIRED = {
    "version", "message_id", "task_id", "correlation_id", "idempotency_key",
    "sender", "recipient", "kind", "status", "created_at_utc",
    "attempt", "payload", "evidence", "retry_policy",
}


class ProtocolError(ValueError):
    """Invalid or unsafe message."""


def _parse_time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ProtocolError("timestamp must be UTC ISO-8601 ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProtocolError("invalid timestamp") from exc
    return parsed


def validate(message, now=None, max_age_seconds=300):
    """Fail closed for unknown/missing fields, stale/future time, or invalid roles."""
    if not isinstance(message, dict) or set(message) != REQUIRED:
        raise ProtocolError("message fields do not match contract")
    if message["version"] != VERSION:
        raise ProtocolError("unsupported version")
    for key in ("message_id", "task_id", "correlation_id", "idempotency_key"):
        if not isinstance(message[key], str) or not ID_RE.fullmatch(message[key]):
            raise ProtocolError("invalid " + key)
    if message["sender"] not in AGENTS or message["recipient"] not in AGENTS:
        raise ProtocolError("unauthorized agent")
    if message["sender"] == message["recipient"]:
        raise ProtocolError("self-addressed message")
    if message["kind"] not in KINDS or message["status"] not in STATUSES:
        raise ProtocolError("invalid kind/status")
    allowed = {"assignment": {"pending"}, "result": {"completed", "failed"},
               "ack": {"accepted"}}
    if message["status"] not in allowed[message["kind"]]:
        raise ProtocolError("kind/status mismatch")
    if type(message["attempt"]) is not int or not 1 <= message["attempt"] <= 3:
        raise ProtocolError("invalid attempt")
    if not isinstance(message["payload"], dict) or not isinstance(message["evidence"], list):
        raise ProtocolError("invalid payload/evidence")
    if message["kind"] == "assignment":
        if not isinstance(message["payload"].get("task"), str) or not message["payload"]["task"].strip():
            raise ProtocolError("assignment requires task")
        if message["evidence"]:
            raise ProtocolError("assignment cannot claim execution evidence")
    if message["kind"] == "result" and not isinstance(message["payload"].get("summary"), str):
        raise ProtocolError("result requires summary")
    if message["kind"] == "ack" and message["payload"] != {"accepted": True}:
        raise ProtocolError("ack requires explicit acceptance")
    if not all(isinstance(e, str) and e.strip() for e in message["evidence"]):
        raise ProtocolError("invalid evidence item")
    retry = message["retry_policy"]
    if not isinstance(retry, dict) or set(retry) != {"max_attempts", "backoff_seconds"}:
        raise ProtocolError("invalid retry policy")
    if type(retry["max_attempts"]) is not int or not 1 <= retry["max_attempts"] <= 3:
        raise ProtocolError("invalid retry limit")
    if type(retry["backoff_seconds"]) is not int or not 0 <= retry["backoff_seconds"] <= 3600:
        raise ProtocolError("invalid retry delay")
    if message["attempt"] > retry["max_attempts"]:
        raise ProtocolError("retry limit exceeded")
    timestamp = _parse_time(message["created_at_utc"])
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ProtocolError("now must be timezone-aware")
    delta = (now.astimezone(timezone.utc) - timestamp).total_seconds()
    if delta < -30 or delta > max_age_seconds:
        raise ProtocolError("future or stale message")
    return True


class InMemoryExchange:
    """Deterministic, isolated state machine; no external actions."""

    def __init__(self):
        self._tasks = {}
        self._messages = {}
        self._keys = {}

    def submit(self, message, now=None):
        validate(message, now=now)
        m = copy.deepcopy(message)
        msg_id = m["message_id"]
        key = m["idempotency_key"]
        if msg_id in self._messages:
            if self._messages[msg_id] != m:
                raise ProtocolError("message ID reused with different content")
            return "duplicate"
        if key in self._keys:
            if self._keys[key] != {k: v for k, v in m.items() if k != "message_id"}:
                raise ProtocolError("idempotency key collision")
            return "duplicate"
        prior = self._tasks.get(m["task_id"])
        kind = m["kind"]
        if prior is None:
            if kind != "assignment":
                raise ProtocolError("task must begin with assignment")
            self._tasks[m["task_id"]] = {
                "status": "pending", "planner": m["sender"], "worker": m["recipient"],
                "correlation_id": m["correlation_id"], "last_time": _parse_time(m["created_at_utc"]),
            }
        else:
            if m["correlation_id"] != prior["correlation_id"]:
                raise ProtocolError("correlation mismatch")
            if _parse_time(m["created_at_utc"]) < prior["last_time"]:
                raise ProtocolError("out-of-order timestamp")
            expected = TRANSITIONS.get(prior["status"], {})
            if kind not in expected:
                raise ProtocolError("out-of-order transition")
            accepted = expected[kind]
            if isinstance(accepted, set):
                if m["status"] not in accepted:
                    raise ProtocolError("invalid result transition")
            elif m["status"] != accepted:
                raise ProtocolError("invalid transition")
            if kind == "result" and (m["sender"], m["recipient"]) != (prior["worker"], prior["planner"]):
                raise ProtocolError("result sender mismatch")
            if kind == "ack" and (m["sender"], m["recipient"]) != (prior["planner"], prior["worker"]):
                raise ProtocolError("ack sender mismatch")
            prior["status"] = m["status"]
            prior["last_time"] = _parse_time(m["created_at_utc"])
        self._messages[msg_id] = m
        self._keys[key] = {k: v for k, v in m.items() if k != "message_id"}
        return "accepted"

    def status(self, task_id):
        item = self._tasks.get(task_id)
        return item["status"] if item else None
