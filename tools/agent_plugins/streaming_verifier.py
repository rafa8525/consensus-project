#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.home() / "consensus-project"
MEMORY = Path.home() / "memory"

QUEUE = MEMORY / "state" / "streaming_verification_queue.json"
TASK_DIR = MEMORY / "tasks" / "streaming_verification"
STATUS = MEMORY / "logs" / "status" / "streaming_verification_agent.md"


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def load_queue():
    try:
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    except Exception:
        return {"pending_count": 0, "pending": []}


def write_task(payload):
    TASK_DIR.mkdir(parents=True, exist_ok=True)

    task_path = TASK_DIR / "current_task.json"

    task = {
        "task_type": "streaming_verification",
        "assigned_agent": "Researcher",
        "generated_utc": iso_now(),
        "status": "ASSIGNED",
        "priority": "HIGH",
        "input_queue": str(QUEUE),

        "objective": (
            "Verify current United States stream-now availability "
            "for every pending movie candidate."
        ),

        "verification_rules": {
            "country": "US",
            "allowed_access": [
                "subscription",
                "included",
                "free",
                "free with ads"
            ],
            "reject": [
                "rent only",
                "buy only",
                "unknown",
                "ambiguous",
                "stale availability"
            ],
            "required_evidence": [
                "platform",
                "checked_date",
                "verification_source",
                "availability"
            ],
            "maximum_age_days": 7,
            "never_guess_platform": True
        },

        "pending": payload.get("pending", [])
    }

    task_path.write_text(
        json.dumps(task, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    return task_path


def write_status(pending_count, task_path):
    STATUS.parent.mkdir(parents=True, exist_ok=True)

    STATUS.write_text(
        "# Streaming Verification Agent\n\n"
        f"- Updated UTC: {iso_now()}\n"
        "- Owner: Researcher Agent\n"
        f"- Pending titles: {pending_count}\n"
        f"- Task: {task_path}\n"
        "- Policy: Never guess streaming availability.\n"
        "- Research backend: NOT YET CONNECTED\n"
        "- State: BLOCKED_NO_WEB_RESEARCH_BACKEND\n",
        encoding="utf-8"
    )


def run():
    payload = load_queue()

    pending = payload.get("pending", [])
    count = len(pending) if isinstance(pending, list) else 0

    if count == 0:
        return [{
            "agent": "Researcher",
            "title": "Streaming verification queue clear",
            "impact": "info",
            "action": "",
            "evidence": [str(QUEUE)],
            "rationale": "No movie candidates currently require verification.",
            "ts": iso_now(),
        }]

    task_path = write_task(payload)
    write_status(count, task_path)

    return [{
        "agent": "Researcher",
        "title": f"Streaming verification assigned: {count} title(s)",
        "impact": "high",
        "action": (
            "Researcher owns the streaming-verification task. "
            "Do not recommend these titles until current U.S. "
            "stream-now evidence has been collected."
        ),
        "evidence": [
            str(task_path),
            str(QUEUE),
            str(STATUS)
        ],
        "rationale": (
            "Streaming availability requires external evidence. "
            "The agent is assigned but intentionally blocked from "
            "inventing results until a real web research backend is connected."
        ),
        "ts": iso_now(),
    }]
