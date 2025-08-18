#!/usr/bin/env python3
import json, sys
from pathlib import Path
from datetime import date
ROOT = Path.home() / "consensus-project"
p = ROOT / "memory" / "logs" / "agents" / "suggestions" / f"suggestions_{date.today().isoformat()}.jsonl"
if not p.exists():
    print("No suggestions file today; nothing to clean."); sys.exit(0)

seen = set()
kept = []
removed = 0
with p.open() as f:
    for line in f:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("title") == "Plugin error":
            removed += 1
            continue
        key = (obj.get("agent"), obj.get("title"))
        if key in seen:
            continue
        seen.add(key)
        kept.append(obj)

tmp = p.with_suffix(".jsonl.tmp")
with tmp.open("w") as out:
    for obj in kept:
        out.write(json.dumps(obj) + "\n")
tmp.replace(p)
print(f"Cleaned {p.name}: kept={len(kept)} removed={removed}")
