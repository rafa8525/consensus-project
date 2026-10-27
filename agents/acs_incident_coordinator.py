#!/usr/bin/env python3
"""ACS incident coordination: safe, durable, no automatic shell execution.

This module is deliberately opt-in until Repair #2's unattended scheduler
gate is verified. It never modifies Git, credentials, schedules or agents.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNERS = {
    "ACS-01": "ACS-01",
    "ACS-02": "ACS-02",
    "ACS-03": "ACS-03",
    "ACS-04": "ACS-04",
    "ACS-05": "ACS-05",
}
REVIEWER = "ACS-03"
SEVERITIES = {"warning", "degraded", "critical"}
MAX_ATTEMPTS = 3
BACKOFF_MINUTES = (5, 30, 180)


def utcnow():
    return datetime.now(timezone.utc)


def parse_utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone required")
    return result.astimezone(timezone.utc)


def safe_code(code):
    if not isinstance(code, str) or not (1 <= len(code) <= 80):
        raise ValueError("invalid incident code")
    if not all(ch.isupper() or ch.isdigit() or ch == "_" for ch in code):
        raise ValueError("incident code must be uppercase and safe")
    return code


def validate_agent(agent):
    if agent not in OWNERS:
        raise ValueError("unknown ACS agent")
    return agent


def incident_key(agent, code):
    return agent + ":" + safe_code(code)


def load(path):
    if not path.exists():
        return {"schema_version": 1, "incidents": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema_version") != 1 or not isinstance(state.get("incidents"), dict):
        raise ValueError("invalid incident state; refusing overwrite")
    return state


def atomic_save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".acs-incidents-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(state, out, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def update(path, agent, code, severity, evidence_utc, *, now=None):
    """Register or refresh an incident; does not execute a repair."""
    validate_agent(agent)
    safe_code(code)
    if severity not in SEVERITIES:
        raise ValueError("invalid severity")
    evidence = parse_utc(evidence_utc)
    now = now or utcnow()
    if evidence > now + timedelta(minutes=5):
        raise ValueError("future evidence timestamp")
    if evidence < now - timedelta(days=30):
        raise ValueError("evidence too old for automatic incident creation")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = load(path)
        key = incident_key(agent, code)
        existing = state["incidents"].get(key)
        if existing and parse_utc(existing["evidence_utc"]) > evidence:
            return existing
        item = existing or {
            "incident_id": key, "component": agent, "code": code,
            "owner": OWNERS[agent], "reviewer": REVIEWER,
            "opened_utc": now.isoformat(), "attempt_count": 0,
            "state": "diagnosis_required", "last_action": "none",
        }
        item["severity"] = severity
        item["evidence_utc"] = evidence.isoformat()
        item["updated_utc"] = now.isoformat()
        # Reopening requires new evidence; never silently close a failure.
        if item["state"] == "verified_resolved":
            item["state"] = "diagnosis_required"
            item["attempt_count"] = 0
        state["incidents"][key] = item
        atomic_save(path, state)
        return item


def request_repair(path, agent, code, action, *, now=None):
    """Record a proposed action only. Explicitly refuses unsafe automation."""
    now = now or utcnow()
    if action not in {"refresh_readonly_cache", "retry_idempotent_feed"}:
        raise ValueError("action is not on the reversible allowlist")
    path = Path(path)
    with path.with_suffix(path.suffix + ".lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = load(path)
        key = incident_key(validate_agent(agent), code)
        item = state["incidents"].get(key)
        if not item:
            raise ValueError("unknown incident")
        if item["attempt_count"] >= MAX_ATTEMPTS:
            raise ValueError("circuit breaker open")
        if item.get("next_retry_utc") and now < parse_utc(item["next_retry_utc"]):
            raise ValueError("backoff in progress")
        item["attempt_count"] += 1
        item["next_retry_utc"] = (now + timedelta(
            minutes=BACKOFF_MINUTES[item["attempt_count"] - 1]
        )).isoformat()
        item["proposed_action"] = action
        item["state"] = "awaiting_simulation_and_review"
        item["last_action"] = "proposal_only"
        item["updated_utc"] = now.isoformat()
        atomic_save(path, state)
        return item


def main():
    parser = argparse.ArgumentParser(description="Safe ACS incident journal")
    parser.add_argument("--state", default="memory/agents/acs_incidents.json")
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("agent", choices=sorted(OWNERS))
    record.add_argument("code")
    record.add_argument("severity", choices=sorted(SEVERITIES))
    record.add_argument("evidence_utc")
    propose = sub.add_parser("propose")
    propose.add_argument("agent", choices=sorted(OWNERS))
    propose.add_argument("code")
    propose.add_argument("action")
    sub.add_parser("status")
    args = parser.parse_args()
    if args.command == "record":
        result = update(args.state, args.agent, args.code, args.severity, args.evidence_utc)
    elif args.command == "propose":
        result = request_repair(args.state, args.agent, args.code, args.action)
    else:
        result = load(Path(args.state))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
