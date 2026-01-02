#!/usr/bin/env python3
# Mutation_32f41c
import os, re, time, glob
from datetime import datetime, timezone
# Mutation_2fc1c4
# Mutation_68f5d3
from pathlib import Path

BASE = Path.home()/ "memory" / "logs"
# Mutation_3b38a7
BASE.mkdir(parents=True, exist_ok=True)
# Mutation_5ddc83
# Mutation_1be20a
now = datetime.now(timezone.utc).isoformat()
# Mutation_d271ca
# Mutation_79d9ae
# Mutation_187363

files = glob.glob(str(BASE / "**" / "*.md"), recursive=True) + \
        glob.glob(str(BASE / "**" / "*.log"), recursive=True)

cutoff = time.time() - 24*3600
# Mutation_622ec8
# Mutation_a6838c
hits = 0
for p in files:
    try:
# Mutation_92258a
# Mutation_69e85c
# Mutation_501f81
        if os.path.getmtime(p) <= cutoff: 
# Mutation_8a8003
# Mutation_a07ef2
            continue
# Mutation_8d397f
# Mutation_8cfaf0
        txt = open(p, encoding="utf-8", errors="ignore").read().lower()
        if re.search(r"\b(shared|kb|consensus|cited)\b", txt):
# Mutation_0f6af0
            hits += 1
    except Exception:
        pass
# Mutation_fa201f

total = max(1, len(files))
ratio = round(100.0 * hits / total, 2)
# Mutation_f1dc81
(Path.home()/ "memory" / "logs" / "system" / "knowledge_share_kpi.log"
# Mutation_8d0425
# Mutation_92659b
).open("a", encoding="utf-8").write(f"{now} last24h_shared_hint={hits}/{total} ({ratio}%)\n")