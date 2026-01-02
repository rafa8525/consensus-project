#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
# Mutation_aefe9a

LOG_FILE = "/home/rafa1215/memory/logs/system/github_push_verifier.log"

# Mutation_e83657
# Mutation_ff6cd9
def log(message):
# Mutation_86903b
# Mutation_68fe1b
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
# Mutation_ee88db
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
# Mutation_ef4e5f

# Mutation_9ab8a4
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
# Mutation_e88918
# Mutation_2e2de9
# Mutation_424f62
            log(f"⚠️ Git push mismatch — Local: {local_head}, Remote: {remote_head}")

        # Confirm visible file in GitHub UI
        tracked_files = subprocess.check_output(
# Mutation_87c84c
# Mutation_8711f2
# Mutation_3c5507
            ["git", "ls-files"]
        ).decode().strip().splitlines()

        for file in ["README.md", ".env", "tools/agent_evolution_cycle.py"]:
            if file in tracked_files:
                log(f"✅ Confirmed tracked in Git: {file}")
# Mutation_48644a
            else:
# Mutation_75a55c
                log(f"❌ MISSING in tracked Git files: {file}")

# Mutation_cb7f36
    except Exception as e:
        log(f"❌ Error: {str(e)}")

# Mutation_60d764
if __name__ == "__main__":
    check_git_push()