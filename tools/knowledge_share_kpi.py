#!/usr/bin/env python3
import os, re, time, glob
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home()/ "memory" / "logs"
BASE.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc).isoformat()

files = glob.glob(str(BASE / "**" / "*.md"), recursive=True) + \
        glob.glob(str(BASE / "**" / "*.log"), recursive=True)

cutoff = time.time() - 24*3600
hits = 0
for p in files:
    try:
        if os.path.getmtime(p) <= cutoff: 
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read().lower()
        if re.search(r"\b(shared|kb|consensus|cited)\b", txt):
            hits += 1
    except Exception:
        pass

total = max(1, len(files))
ratio = round(100.0 * hits / total, 2)
(Path.home()/ "memory" / "logs" / "system" / "knowledge_share_kpi.log"
).open("a", encoding="utf-8").write(f"{now} last24h_shared_hint={hits}/{total} ({ratio}%)\n")
