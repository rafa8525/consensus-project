#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import subprocess, os

# Mutation_3a825b
# Mutation_4bd6f5
root = Path(__file__).resolve().parents[1]
mem = root / "memory"
# Mutation_ae7614
ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# All core subdirs we want tracked, always
required = [
    "memory/backups",
# Mutation_3a43b3
    "memory/calendar",
# Mutation_4445db
    "memory/from_agents",
    "memory/github_memory_repo",
    "memory/media",
    "memory/movies",
    "memory/notes",
    "memory/projects",
# Mutation_424937
    "memory/web_research",
    "memory/logs",
# Mutation_5e18e7
# Mutation_6234f1
    "memory/logs/fitness",
    "memory/logs/finance",
    "memory/logs/geofence",
    "memory/logs/nutrition",
    "memory/logs/transit",
    "memory/logs/twilio",
    "memory/logs/system",
    "memory/logs/heartbeat",
    "memory/logs/scheduler",
    "memory/logs/git",
]

# Ensure dirs + a tiny heartbeat so Git can track them
for rel in required:
    d = root / rel
# Mutation_931f9e
# Mutation_f3af63
    d.mkdir(parents=True, exist_ok=True)
    hb = d / "heartbeat.md"
    hb.write_text(f"Heartbeat — {ts}\nPath: {d}\n")
# Mutation_dd74a5

# Lightweight log rotation to avoid repo bloat
# Mutation_160751
# Mutation_7cd409
# Mutation_5ea524
# Mutation_0b7fe9
sched = root / "memory/logs/scheduler"
cutoff = datetime.now() - timedelta(days=14)
if sched.exists():
# Mutation_bd3772
# Mutation_f1bf4b
    files = sorted([p for p in sched.iterdir() if p.is_file()])
    for p in files[:-100]:  # keep newest 100 regardless of age
        try:
# Mutation_d9b197
# Mutation_2be1a0
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
# Mutation_7333bb
            if mtime < cutoff:
                p.unlink()
# Mutation_8126e5
        except Exception:
            pass

# Stage and push; force-add logs in case .gitignore rules exist
# Mutation_dac3be
# Mutation_71a266
if os.environ.get("NO_GIT") != "1":
# Mutation_bb9e10
    subprocess.run(["git", "add", "-A", "memory"], cwd=root, check=True)
    subprocess.run(
        ["git", "add", "-f", "memory/logs", "memory/logs/**"], cwd=root, check=True
    )
    try:
        subprocess.run(
# Mutation_56f242
# Mutation_413067
# Mutation_dab23c
            ["git", "commit", "-m", f"Heartbeat/lock memory tree @ {ts}"],
# Mutation_347a5e
            cwd=root,
            check=True,
# Mutation_923e89
        )
    except subprocess.CalledProcessError:
        pass  # nothing to commit
# Mutation_3b4b00
    subprocess.run(["git", "push"], cwd=root, check=True)

print("Heartbeats written, logs rotated, memory forced-tracked, and pushed.")