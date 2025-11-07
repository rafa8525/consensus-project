#!/usr/bin/env python3
import os, glob, datetime
from pathlib import Path

HOME = Path.home()
BASE = HOME / "memory" / "logs"
IDX  = BASE / "system" / "agent_log_index.md"
IDX.parent.mkdir(parents=True, exist_ok=True)

paths = glob.glob(str(BASE / "**" / "*.md"), recursive=True) + \
        glob.glob(str(BASE / "**" / "*.log"), recursive=True)
paths = sorted(paths, key=lambda p: os.path.getmtime(p), reverse=True)[:200]

rows = ["# Agent Log Index (latest)"]
for p in paths:
    ts = datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rel = os.path.relpath(p, BASE)
    rows.append(f"- {ts} — {rel}")

IDX.write_text("\n".join(rows) + "\n", encoding="utf-8")
