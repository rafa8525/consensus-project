#!/usr/bin/env python3
"""
Minimal Guard
- Runs a target script (default: generate_weekly_status.py)
- Logs a heartbeat each time it runs
- Safe to schedule hourly
"""
from datetime import datetime
from pathlib import Path
import os, subprocess, shlex

ROOT = Path("/home/rafa1215/consensus-project")
TARGET = os.environ.get(
    "GUARD_TARGET",
    "/home/rafa1215/consensus-project/tools/generate_weekly_status.py"
)
HEART = ROOT / "memory" / "logs" / "system" / "heartbeat" / "guard_heartbeat.log"
def run_target(cmd: str) -> int:
    try:
        return subprocess.call(["python3", cmd])
    except Exception:
        return 99

def log(msg: str) -> None:
    HEART.parent.mkdir(parents=True, exist_ok=True)
    with HEART.open("a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {msg}\n")

def main():
    log(f"guard start; target={TARGET}")
    rc = run_target(TARGET)
    log(f"target rc={rc}")

if __name__ == "__main__":
    main()
