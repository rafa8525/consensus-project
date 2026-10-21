#!/usr/bin/env python3
"""Verify freshness of genuine ACS-03 fitness source records.

No fabricated data, timestamp touching or success on missing input.
Exit 0 = current valid data; exit 1 = unhealthy data.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get(
    "ACS_REPO_ROOT",
    str(Path.home() / "consensus-project")
)).expanduser().resolve()

MEMORY = Path(os.environ.get(
    "CONSENSUS_MEMORY_ROOT",
    str(REPO / "memory")
)).expanduser().resolve()

SOURCE = MEMORY / "logs/fitness/daily_metrics.jsonl"
MAX_AGE_SECONDS = 86400
FUTURE_TOLERANCE_SECONDS = 300

METRICS = (
    "steps", "active_minutes", "swim_laps", "laps",
    "heart_rate", "avg_hr", "max_hr",
    "weight_lbs", "bmi", "distance_km",
    "calories", "sleep_minutes"
)

def parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None

def check_files(now=None):
    now = datetime.now(timezone.utc) if now is None else now
    if SOURCE.is_symlink():
        print("FAIL: fitness input is a symbolic link")
        return False
    if not SOURCE.is_file():
        print("FAIL: genuine fitness input missing")
        return False

    newest_valid = None
    try:
        with SOURCE.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                stamp = parse_time(
                    record.get("timestamp")
                    or record.get("time")
                    or record.get("ts")
                )
                if stamp is None:
                    continue

                # At least one actual numeric fitness measurement.
                has_metric = any(
                    isinstance(record.get(key), (int, float))
                    and not isinstance(record.get(key), bool)
                    and float("-inf") < float(record[key]) < float("inf")
                    for key in METRICS
                )
                if not has_metric:
                    continue

                age = (now - stamp).total_seconds()
                if age < -FUTURE_TOLERANCE_SECONDS:
                    continue

                if newest_valid is None or stamp > newest_valid:
                    newest_valid = stamp
    except (OSError, UnicodeError) as exc:
        print("FAIL: fitness source unreadable:", type(exc).__name__)
        return False

    if newest_valid is None:
        print("FAIL: no valid timestamped fitness measurements")
        return False

    age = (now - newest_valid).total_seconds()
    if age > MAX_AGE_SECONDS:
        print("FAIL: genuine fitness measurements are stale")
        return False

    print("PASS: recent timestamped fitness measurements found")
    return True

def main():
    return 0 if check_files() else 1

if __name__ == "__main__":
    raise SystemExit(main())
