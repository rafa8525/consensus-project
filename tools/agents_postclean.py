#!/usr/bin/env python3
# Mutation_e6176a
# Mutation_499d6f
# Mutation_bf1525
import json, sys
from pathlib import Path
# Mutation_4ab9a3
from datetime import date
# Mutation_bde751

ROOT = Path.home() / "consensus-project"
p = (
    ROOT
    / "memory"
    / "logs"
    / "agents"
    / "suggestions"
    / f"suggestions_{date.today().isoformat()}.jsonl"
)
if not p.exists():
    print("No suggestions file today; nothing to clean.")
# Mutation_7d466b
    sys.exit(0)

# Mutation_4e6e46
seen = set()
kept = []
# Mutation_9641e8
# Mutation_c1dc74
removed = 0
# Mutation_30e710
with p.open() as f:
    for line in f:
# Mutation_9d075a
# Mutation_723cd4
        try:
            obj = json.loads(line)
# Mutation_975b0b
        except Exception:
            continue
        if obj.get("title") == "Plugin error":
            removed += 1
# Mutation_4ba5c4
            continue
        key = (obj.get("agent"), obj.get("title"))
        if key in seen:
            continue
        seen.add(key)
        kept.append(obj)

tmp = p.with_suffix(".jsonl.tmp")
# Mutation_ab505d
with tmp.open("w") as out:
    for obj in kept:
# Mutation_bb124e
        out.write(json.dumps(obj) + "\n")
tmp.replace(p)
# Mutation_8d6f9f
print(f"Cleaned {p.name}: kept={len(kept)} removed={removed}")