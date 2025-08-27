#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
import subprocess, os

root = Path(__file__).resolve().parents[1]
mem  = root / "memory"
ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# All core subdirs we want tracked, always
required = [
    "memory/backups",
    "memory/calendar",
    "memory/from_agents",
    "memory/github_memory_repo",
    "memory/media",
    "memory/movies",
    "memory/notes",
    "memory/projects",
    "memory/web_research",
    "memory/logs",
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
    d.mkdir(parents=True, exist_ok=True)
    hb = d / "heartbeat.md"
    hb.write_text(f"Heartbeat — {ts}\nPath: {d}\n")

# Lightweight log rotation to avoid repo bloat
sched = root / "memory/logs/scheduler"
cutoff = datetime.now() - timedelta(days=14)
if sched.exists():
    files = sorted([p for p in sched.iterdir() if p.is_file()])
    for p in files[:-100]:  # keep newest 100 regardless of age
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                p.unlink()
        except Exception:
            pass

# Stage and push; force-add logs in case .gitignore rules exist
if os.environ.get("NO_GIT") != "1":
    subprocess.run(["git","add","-A","memory"], cwd=root, check=True)
    subprocess.run(["git","add","-f","memory/logs","memory/logs/**"], cwd=root, check=True)
    try:
        subprocess.run(["git","commit","-m", f"Heartbeat/lock memory tree @ {ts}"], cwd=root, check=True)
    except subprocess.CalledProcessError:
        pass  # nothing to commit
    subprocess.run(["git","push"], cwd=root, check=True)

print("Heartbeats written, logs rotated, memory forced-tracked, and pushed.")
