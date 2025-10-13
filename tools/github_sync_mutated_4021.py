# Mutation_e42642
#!/usr/bin/env python3
"""
tools/github_sync.py
Safe GitHub sync runner with logging and retry.
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parent.parent  # consensus-project/
LOG_DIR = BASE / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)

SYNC_LOG = LOG_DIR / "github_sync_log.md"
VISIBILITY_LOG = LOG_DIR / "sync_visibility.log"

# Timestamp helper
def ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def log(path: Path, message: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts()}] {message}\n")

def run_cmd(cmd, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=str(BASE),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            if result.returncode == 0:
                log(SYNC_LOG, f"✅ {cmd}\n{result.stdout.strip()}")
                return True
            else:
                log(SYNC_LOG, f"⚠️ Attempt {attempt}: {cmd}\n{result.stdout.strip()}")
        except Exception as e:
            log(SYNC_LOG, f"❌ Exception running {cmd}: {e}")
        time.sleep(delay)
    return False

def main():
    log(SYNC_LOG, "🔄 GitHub sync started")
    log(VISIBILITY_LOG, "GitHub sync run triggered")

    # Ensure git knows who we are
    run_cmd('git config user.name "ConsensusBot"')
    run_cmd('git config user.email "rafa1215@users.noreply.github.com"')

    # Stage changes
    if not run_cmd("git add -A"):
        log(SYNC_LOG, "❌ Failed to stage files")
        return 2

    # Commit (ignore if nothing to commit)
    commit_cmd = 'git commit -m "Automated sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true'
    run_cmd(commit_cmd)

    # Push
    if run_cmd("git push origin v1.1-dev"):
        log(SYNC_LOG, "✅ GitHub sync completed successfully")
        log(VISIBILITY_LOG, "GitHub sync succeeded")
        return 0
    else:
        log(SYNC_LOG, "❌ GitHub sync failed after retries")
        log(VISIBILITY_LOG, "GitHub sync failed")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())