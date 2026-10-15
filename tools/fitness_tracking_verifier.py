#!/usr/bin/env python3
"""Fail closed unless real, timestamped fitness source measurements are recent.

This verifies data freshness, not device authentication. Pixel Watch is the
preferred source; upstream ingestion/authorization is a separate responsibility.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

MAX_AGE_SECONDS = 24 * 3600
FUTURE_TOLERANCE_SECONDS = 300
METRICS = frozenset((
    "steps", "step_count", "active_minutes", "mvpa_minutes", "zone_minutes",
    "swim_laps", "laps", "pool_laps", "heart_rate", "avg_hr",
    "average_hr", "heart_rate_avg", "max_hr", "heart_rate_max",
    "weight_lbs", "bmi", "distance_km", "calories", "sleep_minutes",
))

def source_path() -> Path:
    repo = Path(os.environ.get("ACS_REPO_ROOT", str(Path.home() / "consensus-project")))
    memory = Path(os.environ.get("CONSENSUS_MEMORY_ROOT", str(repo / "memory")))
    return memory.expanduser().resolve() / "logs/fitness/daily_metrics.jsonl"

def timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None

def has_measurement(record: dict) -> bool:
    return any(
        key in METRICS and type(value) in (int, float)
        and math.isfinite(value) and value >= 0
        for key, value in record.items()
    )

def check_files(now: datetime | None = None) -> bool:
    now = datetime.now(timezone.utc) if now is None else now
    source = source_path()
    if not source.is_file() or source.is_symlink():
        print("FAIL: genuine fitness source missing")
        return False
    recent = False
    try:
        with source.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict) or not has_measurement(record):
                    continue
                stamp = timestamp(record.get("timestamp") or record.get("time") or record.get("ts"))
                if stamp is None:
                    continue
                age = (now - stamp).total_seconds()
                if -FUTURE_TOLERANCE_SECONDS <= age <= MAX_AGE_SECONDS:
                    recent = True
                    break
    except (OSError, UnicodeError):
        print("FAIL: fitness source cannot be read")
        return False
    print("PASS: recent numeric fitness source record found" if recent
          else "FAIL: no recent valid fitness source record")
    return recent

def main() -> int:
    return 0 if check_files() else 1

if __name__ == "__main__":
    raise SystemExit(main())
