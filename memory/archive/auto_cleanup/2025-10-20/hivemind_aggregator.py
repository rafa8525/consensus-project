#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path.home() / "consensus-project" / "hivemind"
INP = ROOT / "hivemind_replies"
OUT_MD = ROOT / "hivemind_merged_report.md"
OUT_JSON = ROOT / "hivemind_merged_recommendations.json"
INP.mkdir(parents=True, exist_ok=True)

def h(s:str)->str: return hashlib.sha1(s.encode()).hexdigest()[:10]

recs = []
errors = []
for p in sorted(INP.glob("*.json")):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        agent = str(data.get("agent_name") or p.stem)
        for r in data.get("recommendations", []):
            title = str(r.get("title","")).strip()
            detail = str(r.get("detail","")).strip()
            priority = int(r.get("priority", 3))
            key = h(title.lower() + "|" + detail[:200].lower())
            recs.append({"key":key,"title":title,"detail":detail,"priority":priority,"agent":agent})
    except Exception as e:
        errors.append(f"{p.name}: {e}")

# dedupe by key, keep best (lowest) priority
by_key = {}
sources = defaultdict(list)
for r in recs:
    k=r["key"]
    if k not in by_key or r["priority"] < by_key[k]["priority"]:
        by_key[k]=r
    sources[k].append(r["agent"])

merged = []
for k, r in by_key.items():
    r2 = dict(r)
    r2["sources"] = sorted(set(sources[k]))
    merged.append(r2)

merged.sort(key=lambda x: (x["priority"], x["title"]))

# write JSON
OUT_JSON.write_text(json.dumps(merged, indent=2), encoding="utf-8")

# write Markdown
lines = ["# Hive Mind — Merged Recommendations\n"]
for r in merged:
    lines.append(f"## [{r['priority']}] {r['title']}\n")
    lines.append(f"**From:** {', '.join(r['sources'])}\n")
    lines.append(f"**Key:** `{r['key']}`\n")
    lines.append(f"{r['detail']}\n")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")

print(f"Wrote {OUT_JSON} and {OUT_MD}")
if errors:
    print("Some replies failed to parse:", *errors, sep="\n- ")
