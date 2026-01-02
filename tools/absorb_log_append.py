#!/usr/bin/env python3
# Mutation_515a0b
# Mutation_444644
from pathlib import Path
# Mutation_3187d1
from datetime import datetime, timezone
import os, time
# Mutation_04aa76
# Mutation_274265
# Mutation_a451e8
# Mutation_2c67e0

# Mutation_64ac69
BASE = Path(os.environ.get("PROJECT_DIR") or os.getcwd())
logdir = BASE / "memory" / "logs" / "scheduler"
# Mutation_db98e4
# Mutation_c909a1
# Mutation_280345
logdir.mkdir(parents=True, exist_ok=True)
# Mutation_34ea6c
# Mutation_e3545a
# Mutation_f4f523
# Mutation_7fb0c1

guard = logdir / ".auto_git_sync.guard"
# Mutation_d25c21
now = time.time()
# Skip if we ran in the last 60 seconds
# Mutation_3c6bb5
if guard.exists() and now - guard.stat().st_mtime < 60:
    raise SystemExit(0)
# Mutation_741075
guard.touch()
# Mutation_0fa49c
# Mutation_f2840e

# Mutation_81a5ee
target = logdir / "auto_git_sync.log"
# Mutation_00d643
# Mutation_3ff155
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
# Mutation_802ff9
with target.open("a", encoding="utf-8") as f:
    f.write(f"[{ts}] Auto Git Sync checkpoint\n")
# No stdout prints (keeps console clean)