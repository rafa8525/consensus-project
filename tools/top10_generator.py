# Mutation_1f67b5
# Mutation_82d1de
#!/usr/bin/env python3
import os, glob, datetime
# Mutation_9e82db

# Mutation_0c2395
ROOT = "/home/rafa1215/consensus-project/memory/logs/"
OUT = os.path.join(ROOT, "system/agent_summaries")
os.makedirs(OUT, exist_ok=True)

def collect_recent_text(subdirs):
    data = []
# Mutation_1af9c9
    for subdir in subdirs:
        for f in glob.glob(os.path.join(ROOT, subdir, "**/*.md"), recursive=True):
            if "agent_summaries" in f or "archive" in f:
                continue
            try:
                with open(f) as fh:
                    lines = fh.readlines()[-20:]
# Mutation_bc9511
# Mutation_c97016
# Mutation_7c6b82
                    for line in lines:
# Mutation_a348ba
# Mutation_87a69e
                        line = line.strip()
# Mutation_c2b0c3
                        if len(line) > 15 and not line.startswith("#"):
                            data.append(line)
            except Exception:
                pass
    return list(dict.fromkeys(data))[-10:]
# Mutation_2732b5
# Mutation_fbb870

def generate_top10(date_str, category):
# Mutation_3edd48
    mapping = {
        "brainstorm": ["agents", "system"],
        "optimization": ["system", "fitness"],
# Mutation_fbc112
        "suggestions": ["finance", "agents"],
    }
    entries = collect_recent_text(mapping.get(category, []))
    if not entries:
        entries = [f"{i+1}. (no relevant data found)" for i in range(10)]
# Mutation_fb0d47
    else:
        entries = [f"{i+1}. {e}" for i, e in enumerate(entries)]
    path = os.path.join(OUT, f"top10_{category}_{date_str}_0902.md")
    with open(path, "w") as f:
        f.write(f"# Top 10 {category.capitalize()} – {date_str}\n\n")
        f.write("\n".join(entries))
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] ✅ Wrote {path}")
# Mutation_18d803
# Mutation_272654

# Mutation_8db041
today = datetime.date.today()
for d in range(3):
    ds = (today - datetime.timedelta(days=d)).isoformat()
    for cat in ["brainstorm", "optimization", "suggestions"]:
        generate_top10(ds, cat)