#!/usr/bin/env python3
"""
absorb_guard.py
Protects absorption + git push with retries, checkpointing, and self-repair.
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Config
PROJECT_ROOT = Path.home() / "consensus-project"
ABSORB_CMD = str(PROJECT_ROOT / "tools" / "absorb_once.sh")
CHECKPOINT_FILE = PROJECT_ROOT / "memory" / "logs" / "system" / "last_absorb_status.json"
MAX_RETRIES = 3
RETRY_DELAY_BASE = 5  # seconds

def run_command(cmd):
    """Run shell command, capture output."""
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, cwd=PROJECT_ROOT
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def write_checkpoint(status, details=""):
    """Save last run status to checkpoint file."""
    checkpoint = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "details": details
    }
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)
    print(f"[checkpoint] {checkpoint}")

def clean_index_lock():
    """Remove stale git index.lock if exists."""
    lockfile = PROJECT_ROOT / ".git" / "index.lock"
    if lockfile.exists():
        lockfile.unlink()
        print("[repair] Removed stale .git/index.lock")

def main():
    print(f"[guard] Starting absorb_guard at {datetime.utcnow().isoformat()}Z")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[guard] Attempt {attempt}/{MAX_RETRIES}")

        # Clean stale locks before each try
        clean_index_lock()

        rc, out, err = run_command(ABSORB_CMD)
        if rc == 0:
            print("[guard] SUCCESS")
            write_checkpoint("success", out)
            return 0

        # Failed attempt
        print(f"[guard] FAIL rc={rc}")
        if err:
            print(f"[stderr]\n{err}")
        if out:
            print(f"[stdout]\n{out}")

        # Exponential backoff before retry
        delay = RETRY_DELAY_BASE * attempt
        print(f"[guard] Sleeping {delay}s before retry...")
        time.sleep(delay)

    # If we get here → all retries failed
    print("[guard] ERROR: All attempts failed")
    write_checkpoint("failure", err or "unknown error")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
