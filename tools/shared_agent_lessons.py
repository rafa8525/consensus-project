#!/usr/bin/env python3
"""Minimal, bounded and auditable cross-agent lessons. No autonomous actions.

ACS-01 records fixed lessons only from actual failed child cycle outcomes.
ACS-01's next evaluator run reads these structured records and creates review
recommendations. The mechanism does not claim independent learning or repair.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

LESSON_FILE = Path("memory/logs/agents/shared_lessons.jsonl")
MAX_ROWS = 5000
MAX_AGE_DAYS = 30
# Strict allow-list: do not record exception messages, logs or secrets.
CATALOG = {
    "ACS-02": ("absorption_not_verified",
               "Verify ACS-02 absorption evidence; do not advertise an unverified knowledge refresh."),
    "ACS-03": ("fitness_cycle_degraded",
               "Inspect ACS-03 verified fitness pipeline results before trusting the health snapshot."),
    "ACS-04": ("infrastructure_degraded",
               "Review ACS-04 infrastructure status and verify recovery before treating infrastructure as healthy."),
    "ACS-05": ("continuity_degraded",
               "Review ACS-05 continuity status and preserve the existing SMS safety gate."),
}

def lessons_path(repo: Path) -> Path:
    return repo / LESSON_FILE

def produce(repo: Path, results: dict, *, now: datetime | None = None) -> dict:
    """Publish one bounded lesson per failing agent per cycle.

    Caller supplies fresh supervisor results; only explicit unhealthy outcomes
    are accepted. No source code or external systems are modified.
    """
    now = now or datetime.now(timezone.utc)
    candidates = []
    for agent, (incident, advice) in CATALOG.items():
        entry = results.get(agent.lower().replace("-", "_"))
        if not isinstance(entry, dict):
            continue
        if entry.get("ok") is False and entry.get("status") in (
                "warning", "critical", "execution_failure"):
            candidates.append({
                "producer": agent, "incident": incident,
                "recommendation": advice,
                "observed_utc": now.astimezone(timezone.utc).isoformat(),
            })
    if not candidates:
        return {"published": 0}
    target = lessons_path(repo)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Single append, no truncate or rewritten historical records.
    with target.open("a", encoding="utf-8") as f:
        for item in candidates:
            f.write(json.dumps(item, sort_keys=True) + "\n")
    return {"published": len(candidates)}

def consume(repo: Path, *, now: datetime | None = None) -> list[dict]:
    """ACS-01 evaluator retrieves recent lessons to prepare review advice.

    Only allow-listed advice and source-agent signatures survive validation.
    Does not run scripts, write files, send alerts, or trust arbitrary content.
    """
    now = now or datetime.now(timezone.utc)
    threshold = now.astimezone(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    latest: dict[str, dict] = {}
    try:
        with lessons_path(repo).open(encoding="utf-8") as f:
            for index, line in enumerate(f):
                if index >= MAX_ROWS:
                    break
                try:
                    item = json.loads(line)
                    agent = item["producer"]
                    incident, advice = CATALOG[agent]
                    stamp = datetime.fromisoformat(item["observed_utc"].replace("Z", "+00:00"))
                    if stamp.tzinfo is None or not threshold <= stamp <= now + timedelta(minutes=2):
                        continue
                    if item.get("incident") != incident or item.get("recommendation") != advice:
                        continue
                    prev = latest.get(agent)
                    if prev is None or item["observed_utc"] > prev["observed_utc"]:
                        latest[agent] = {"producer": agent, "incident": incident,
                                         "recommendation": advice,
                                         "observed_utc": item["observed_utc"]}
                except (KeyError, ValueError, TypeError, AttributeError):
                    continue
    except OSError:
        return []
    return [latest[k] for k in sorted(latest)]
