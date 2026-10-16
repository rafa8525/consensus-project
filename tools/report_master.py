#!/usr/bin/env python3
"""Run required reporting jobs; fail the cycle if any report fails."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
JOBS = ("generate_weekly_report.py", "summarize_agent_logs.py")

def run(script: str) -> bool:
    """Return True only for an actually successful child process."""
    candidate = BASE / script
    if not candidate.is_file():
        print(f"REPORT_FAILURE missing_job={script}", file=sys.stderr)
        return False
    try:
        result = subprocess.run([sys.executable, str(candidate)], cwd=BASE.parent, timeout=900, check=False)
    except (OSError, subprocess.TimeoutExpired):
        print(f"REPORT_FAILURE execution_error={script}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(f"REPORT_FAILURE nonzero_exit={script}", file=sys.stderr)
        return False
    return True

def main() -> int:
    results = [run(script) for script in JOBS]
    if all(results):
        print("Reports and agent summaries completed successfully.")
        return 0
    print("REPORT_FAILURE one or more required reporting jobs failed", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
