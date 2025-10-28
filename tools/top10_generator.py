#!/usr/bin/env python3
import os, glob, datetime

ROOT = "/home/rafa1215/consensus-project/memory/logs/"
OUT = os.path.join(ROOT, "system/agent_summaries")
os.makedirs(OUT, exist_ok=True)

def collect_recent_text(subdirs):
    data = []
    for subdir in subdirs:
        for f in glob.glob(os.path.join(ROOT, subdir, "**/*.md"), recursive=True):
            if "agent_summaries" in f or "archive" in f:
                continue
            try:
                with open(f) as fh:
                    lines = fh.readlines()[-20:]
                    for line in lines:
                        line = line.strip()
                        if len(line) > 15 and not line.startswith("#"):
                            data.append(line)
            except Exception:
                pass
    return list(dict.fromkeys(data))[-10:]

def generate_top10(date_str, category):
    mapping = {
        "brainstorm": ["agents", "system"],
        "optimization": ["system", "fitness"],
        "suggestions": ["finance", "agents"],
    }
    entries = collect_recent_text(mapping.get(category, []))
    if not entries:
        entries = [f"{i+1}. (no relevant data found)" for i in range(10)]
    else:
        entries = [f"{i+1}. {e}" for i, e in enumerate(entries)]
    path = os.path.join(OUT, f"top10_{category}_{date_str}_0902.md")
    with open(path, "w") as f:
        f.write(f"# Top 10 {category.capitalize()} – {date_str}\n\n")
        f.write("\n".join(entries))
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] ✅ Wrote {path}")

today = datetime.date.today()
for d in range(3):
    ds = (today - datetime.timedelta(days=d)).isoformat()
    for cat in ["brainstorm", "optimization", "suggestions"]:
        generate_top10(ds, cat)
