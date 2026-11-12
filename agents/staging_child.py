"""Disposable staging child for real OS-process crash injection.

Only local synthetic SQLite DBs, no network, external services, or production.
The supervisor must run this as a separate process.
"""
import os
import sys

from agents.phase3_pipeline import SimulatedEvidencePipeline
from agents.phase5_durable import DurableMockRegistry


def main(mode, folder):
    task_db = os.path.join(folder, "tasks.sqlite")
    memory_db = os.path.join(folder, "memory.sqlite")
    event_db = os.path.join(folder, "events.sqlite")

    def task_handler(task):
        if mode == "kill_task":
            os._exit(71)
        return "mock-task-completed"

    pipeline = SimulatedEvidencePipeline(
        task_db, memory_db, {"executor": task_handler}, simulation=True)
    try:
        task = pipeline.dispatch("staging.task1", "executor", "synthetic work")
        if task["state"] != "completed" or task["memory_status"] != "recorded":
            raise RuntimeError("staging prerequisite not completed")
    finally:
        pipeline.close()

    def delivery_handler(payload):
        if mode == "kill_notification":
            os._exit(72)
        return "mock-notification-sent"

    registry = DurableMockRegistry(event_db, simulation=True)
    registry.register(adapter_id="notifications.mock", capability="notifications",
                      workflow_key="existing.status.summary", owner="acs-02",
                      permissions={"notify_mock"}, handler=delivery_handler)
    try:
        status = registry.dispatch(
            adapter_id="notifications.mock", principal="acs-02",
            permission="notify_mock", event_id="staging.event1",
            payload={"synthetic_value": "synthetic task finished"})
        if status["status"] != "delivered":
            raise RuntimeError("unexpected mock notification outcome")
    finally:
        registry.close()


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("kill_task", "kill_notification", "success"):
        raise SystemExit("usage: python -m agents.staging_child <mode> <sandbox-folder>")
    main(sys.argv[1], sys.argv[2])
