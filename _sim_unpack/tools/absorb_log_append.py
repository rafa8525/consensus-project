#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import os, time

BASE = Path(os.environ.get("PROJECT_DIR") or os.getcwd())
logdir = BASE / "memory" / "logs" / "scheduler"
logdir.mkdir(parents=True, exist_ok=True)

guard = logdir / ".auto_git_sync.guard"
now = time.time()
# Skip if we ran in the last 60 seconds
if guard.exists() and now - guard.stat().st_mtime < 60:
    raise SystemExit(0)
guard.touch()

target = logdir / "auto_git_sync.log"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
with target.open("a", encoding="utf-8") as f:
    f.write(f"[{ts}] Auto Git Sync checkpoint\n")
# No stdout prints (keeps console clean)
