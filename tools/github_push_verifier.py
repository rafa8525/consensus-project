#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

LOG_FILE = "/home/rafa1215/memory/logs/system/github_push_verifier.log"

def log(message):
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")

def check_git_push():
    try:
        os.chdir("/home/rafa1215/consensus-project")

        # Get latest commit
        commit_hash = subprocess.check_output(
            ["git", "log", "-1", "--format=%H"]
        ).decode().strip()

        commit_msg = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"]
        ).decode().strip()

        remote_info = subprocess.check_output(
            ["git", "remote", "-v"]
        ).decode().strip()

        # Compare local and remote HEADs
        local_head = subprocess.check_output(
            ["git", "rev-parse", "@"]
        ).decode().strip()

        remote_head = subprocess.check_output(
            ["git", "rev-parse", "@{u}"]
        ).decode().strip()

        if local_head == remote_head:
            log(f"✅ Git push verified — Commit: {commit_hash}, Msg: '{commit_msg}'")
        else:
            log(f"⚠️ Git push mismatch — Local: {local_head}, Remote: {remote_head}")

        # Confirm visible file in GitHub UI
        tracked_files = subprocess.check_output(
            ["git", "ls-files"]
        ).decode().strip().splitlines()

        for file in ["README.md", ".env", "tools/agent_evolution_cycle.py"]:
            if file in tracked_files:
                log(f"✅ Confirmed tracked in Git: {file}")
            else:
                log(f"❌ MISSING in tracked Git files: {file}")

    except Exception as e:
        log(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_git_push()
