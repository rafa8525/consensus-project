"""Complete isolated ACS development demo: coordination, memory, evaluation, integration.

Runs only explicit mock handlers and fixed synthetic fixtures. No production
schedulers, external APIs, agent authentication or real personal data.
"""
import os
from datetime import datetime, timezone

from agents.phase2_protocol import ProtocolError
from agents.phase3_pipeline import SimulatedEvidencePipeline
from agents.phase4_observation import evaluate_observed
from agents.phase5_durable import DurableMockRegistry


def build_registry(db_path, calls):
    registry = DurableMockRegistry(db_path, simulation=True)
    registry.register(
        adapter_id="notifications.mock",
        capability="notifications",
        workflow_key="existing.status.summary",
        owner="acs-02",
        permissions={"notify_mock"},
        handler=lambda payload: calls.append(dict(payload)) or "synthetic-notification"
    )
    return registry


def _demo_measurements(now):
    stamp = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    base = {"success_rate": 1.0, "latency_ms": 120.0,
            "resource_units": 12.0, "duplicate_effects": 0,
            "unauthorized_writes": 0, "unverified_recoveries": 0,
            "private_data_leaks": 0}
    candidate = dict(base, latency_ms=80.0, resource_units=10.0)
    def record(sha, metrics):
        return {"fixture_id": "system-demo.v1", "commit_sha": sha,
                "generated_at_utc": stamp, "sample_count": 10,
                "metrics": dict(metrics)}
    fixture = {
        "baseline": record("a" * 40, base),
        "candidate": record("b" * 40, candidate),
        "proposal": {"id": "routing.v1", "target": "routing",
                     "description": "Synthetic offline change only",
                     "rollback_ref": "baseline.v1", "risk": "low",
                     "operations": ["offline_evaluate"]},
    }
    observer = {
        side: {"fixture_id": rec["fixture_id"], "commit_sha": rec["commit_sha"],
               "sample_count": rec["sample_count"], "metrics": dict(rec["metrics"]),
               "observer_id": "offline-test-harness-v1"}
        for side, rec in (("baseline", fixture["baseline"]),
                          ("candidate", fixture["candidate"]))
    }
    return fixture, observer


def run_mock_workflow(folder, *, simulation=False, now=None):
    """Run and restart real SQLite mock components without external side effects."""
    if simulation is not True:
        raise ProtocolError("simulation=True required")
    if not isinstance(folder, (str, os.PathLike)) or not os.path.isdir(folder):
        raise ProtocolError("existing sandbox directory required")
    now = now or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ProtocolError("timezone-aware clock required")
    task_db = os.path.join(folder, "task-journal.sqlite")
    memory_db = os.path.join(folder, "evidence-memory.sqlite")
    events_db = os.path.join(folder, "event-journal.sqlite")
    execution_calls, notification_calls = [], []
    handlers = {"executor": lambda task: execution_calls.append(task) or "mock-completed"}

    pipeline = SimulatedEvidencePipeline(task_db, memory_db, handlers, simulation=True)
    registry = build_registry(events_db, notification_calls)
    try:
        first = pipeline.dispatch("task.demo1", "executor", "synthetic work")
        notification = registry.dispatch(
            adapter_id="notifications.mock", principal="acs-02",
            permission="notify_mock", event_id="event.demo1",
            payload={"synthetic_value": "task completed"})
        memory_count = len(pipeline.memory.for_task("task.demo1"))
    finally:
        pipeline.close()
        registry.close()

    # Reopen SQLite components as after a restart, with new mock handlers.
    pipeline = SimulatedEvidencePipeline(task_db, memory_db, handlers, simulation=True)
    registry = build_registry(events_db, notification_calls)
    try:
        replay_task = pipeline.dispatch("task.demo1", "executor", "synthetic work")
        replay_notification = registry.dispatch(
            adapter_id="notifications.mock", principal="acs-02",
            permission="notify_mock", event_id="event.demo1",
            payload={"synthetic_value": "task completed"})
        memory_count_restart = len(pipeline.memory.for_task("task.demo1"))
    finally:
        pipeline.close()
        registry.close()

    fixture, observations = _demo_measurements(now)
    evaluation = evaluate_observed(fixture, observations, now=now, simulation=True)

    return {
        "task_first_status": first["state"],
        "notification_first_status": notification["status"],
        "task_replay_executed": replay_task["executed"],
        "notification_replay_executed": replay_notification["executed"],
        "task_execution_count": len(execution_calls),
        "notification_count": len(notification_calls),
        "evidence_count_before": memory_count,
        "evidence_count_after": memory_count_restart,
        "candidate_decision": evaluation["decision"],
        "candidate_deployed": evaluation["deployment_allowed"],
        "mode": "synthetic-isolated-demo",
    }
