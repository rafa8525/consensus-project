#!/usr/bin/env python3
"""Verify fitness data freshness for ACS-03.

Exit 0 only when at least one fitness log file was modified within the
last 24 hours. Exit 1 for missing, stale, or future-dated input.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(os.environ.get("ACS_REPO_ROOT", "/home/rafa1215/consensus-project"))
FITNESS_DIR = BASE / "memory/logs/fitness"
SYSTEM_LOG = BASE / "memory/logs/system/fitness_integration.log"
MAX_AGE_SECONDS = 24 * 60 * 60
FUTURE_TOLERANCE_SECONDS = 5 * 60


def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    SYSTEM_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SYSTEM_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def check_files(now: float | None = None) -> bool:
    now = time.time() if now is None else now
    if not FITNESS_DIR.is_dir():
        log("FAIL Fitness log directory missing.")
        return False

    files = [path for path in FITNESS_DIR.iterdir() if path.is_file() and not path.is_symlink()]
    if not files:
        log("FAIL No fitness log files found.")
        return False

    try:
        latest = max(path.stat().st_mtime for path in files)
    except OSError as exc:
        log(f"FAIL Cannot read fitness log timestamps: {type(exc).__name__}")
        return False

    age_seconds = now - latest
    age_minutes = age_seconds / 60
    if age_seconds < -FUTURE_TOLERANCE_SECONDS:
        log(f"FAIL Fitness log timestamp is {abs(age_minutes):.1f} min in the future; clock or sync anomaly.")
        return False
    if age_seconds > MAX_AGE_SECONDS:
        log(f"FAIL Last fitness update older than 24 hours ({age_minutes:.1f} min ago).")
        return False

    log(f"PASS Fitness logs are current (updated {age_minutes:.1f} min ago).")
    return True


def main() -> int:
    log("---- Starting Fitness Integration Verification ----")
    passed = check_files()
    log("---- Verification complete: PASS ----" if passed else "---- Verification complete: ATTENTION REQUIRED ----")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
