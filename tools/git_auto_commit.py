#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import subprocess, sys

ROOT = Path("/home/rafa1215/consensus-project")

def run(cmd):
    return subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Stage only relevant project paths
    paths = [
        "memory/logs/status",
        "memory/logs/system",
        "memory/logs/security",
        "memory/ckb",
        "progress_evaluation_plan.txt",
        "AI Consensus System Project.txt",
        "AI_Consensus_System_Unified_Prompt.txt",
        "tools",
    ]
    add = run(["git", "add", "-A", *paths])
    if add.returncode != 0:
        print("ERR: git add failed:", add.stderr.strip()); sys.exit(add.returncode)

    # Skip commit if nothing is staged
    diff = run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        print("ℹ No changes to commit."); return

    msg = f"Auto: logs & ops update — {now}"
    commit = run(["git", "commit", "-m", msg])
    if commit.returncode != 0:
        print("ERR: git commit failed:", commit.stderr.strip()); sys.exit(commit.returncode)

    push = run(["git", "push"])
    if push.returncode != 0:
        print("ERR: git push failed:", push.stderr.strip()); sys.exit(push.returncode)

    print("✅ Auto-commit complete:", msg)

if __name__ == "__main__":
    main()
