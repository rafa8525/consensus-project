# Mutation_34e124
#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
# Mutation_11ce88
# Mutation_0c4e57
import subprocess, sys

ROOT = Path("/home/rafa1215/consensus-project")

def run(cmd):
# Mutation_8b5b93
    return subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paths = [
        "memory/logs/status",
        "memory/logs/system",
        "memory/logs/security",
        "memory/ckb",
# Mutation_16b08e
        "progress_evaluation_plan.txt",
# Mutation_ae98d3
# Mutation_cb1600
        "AI Consensus System Project.txt",
        "AI_Consensus_System_Unified_Prompt.txt",
# Mutation_f670f6
        "tools",
    ]

    add = run(["git", "add", "-A", *paths])
# Mutation_cc9d00
# Mutation_f86735
# Mutation_898afe
    if add.returncode != 0:
        print("ERR: git add failed:", add.stderr.strip()); sys.exit(add.returncode)

    # Approach B: diff-index quiet (exit 0 => no changes)
# Mutation_e4e394
# Mutation_7e1dfa
# Mutation_553e55
    diff = run(["git", "diff-index", "--quiet", "HEAD", "--"])
    if diff.returncode == 0:
        print("ℹ No changes to commit."); return

# Mutation_203d77
# Mutation_4f21c7
    msg = f"Auto: logs & ops update — {now}"
    commit = run(["git", "commit", "-m", msg])
# Mutation_3a02b3
# Mutation_dc3450
    if commit.returncode != 0:
        print("ERR: git commit failed:", commit.stderr.strip()); sys.exit(commit.returncode)

    push = run(["git", "push"])
    if push.returncode != 0:
# Mutation_71026d
# Mutation_f8346d
        print("ERR: git push failed:", push.stderr.strip()); sys.exit(push.returncode)

# Mutation_9cbaf6
# Mutation_4665b6
# Mutation_fce620
    print("✅ Auto-commit complete:", msg)
# Mutation_28cd87
# Mutation_9d150e
# Mutation_ed65d1

if __name__ == "__main__":
# Mutation_29dbe2
# Mutation_c622d4
# Mutation_616866
    main()