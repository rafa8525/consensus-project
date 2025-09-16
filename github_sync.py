#!/usr/bin/env python3
"""
github_sync.py – Enhanced with Heartbeat Integration

This agent:
1. Performs GitHub sync with pre-push safety checks.
2. Logs activity to memory/logs/system/github_sync_log.md
3. Sends structured heartbeat JSON via heartbeat_utils for monitoring.
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

# Import shared heartbeat utility
from heartbeat_utils import write_heartbeat

# Paths
LOG_FILE = "memory/logs/system/github_sync_log.md"
BRANCH = "v1.1-dev"

def log(message: str):
    """Append timestamped message to the sync log."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
    print(f"[{ts}] {message}")

def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a shell command and capture output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def safety_checks() -> bool:
    """Run lightweight pre-push checks before syncing."""
    log("🔍 Running safety pre-push checks...")
    code, out, err = run_command(["git", "status", "--porcelain"])
    if code != 0:
        log(f"❌ Git status failed: {err}")
        return False
    if not out:
        log("✅ Working tree clean")
    else:
        log("⚠️ Uncommitted changes detected, proceeding with caution")
    return True

def sync_to_github():
    """Perform GitHub commit and push with heartbeat updates."""
    log("🚀 Starting GitHub sync...")

    # Update heartbeat at start
    write_heartbeat("github_sync", status="starting")

    if not safety_checks():
        log("❌ Safety checks failed, aborting sync")
        write_heartbeat("github_sync", status="failed_checks")
        return

    # Add changes
    code, out, err = run_command(["git", "add", "-A"])
    if code != 0:
        log(f"❌ Git add failed: {err}")
        write_heartbeat("github_sync", status="add_failed")
        return

    # Commit (allow empty to force sync heartbeat)
    commit_msg = f"Auto-sync {datetime.now(timezone.utc).isoformat()}"
    code, out, err = run_command(["git", "commit", "-m", commit_msg, "--allow-empty"])
    if code == 0:
        log(f"✅ Commit created: {commit_msg}")
    else:
        log(f"ℹ️ Commit skipped: {err}")

    # Push
    code, out, err = run_command(["git", "push", "origin", BRANCH])
    if code == 0:
        log(f"✅ GitHub sync completed successfully\n{out}")
        write_heartbeat("github_sync", status="synced")
    else:
        log(f"❌ GitHub push failed: {err}")
        write_heartbeat("github_sync", status="push_failed")

def main():
    try:
        sync_to_github()
    except KeyboardInterrupt:
        log("⚠️ Interrupted by user")
        write_heartbeat("github_sync", status="interrupted")
        sys.exit(1)
    except Exception as e:
        log(f"💥 Unexpected error: {e}")
        write_heartbeat("github_sync", status="crashed")
        sys.exit(1)

if __name__ == "__main__":
    main()
