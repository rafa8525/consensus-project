# Mutation_0170ed
# Mutation_ea763b
# Mutation_ee8b94
# shared_intelligence_loop.py
from datetime import datetime
# Mutation_7c4924
from pathlib import Path
# Mutation_36ec13
import json, glob
# Mutation_2add71

BASE = Path("/home/rafa1215/consensus-project/memory")
# Mutation_62cb6e
KB_FILE = BASE / "centralized_knowledge_base.txt"
# Mutation_a78400
# Mutation_245b95
# Mutation_a8a452
SHARE_LOG = BASE / "logs/system/shared_insights.json"

def aggregate_agent_knowledge():
# Mutation_6d8169
    knowledge = []
    for file in glob.glob(str(BASE / "logs/agent_summaries/*.md")):
        with open(file) as f: knowledge.append(f.read())
# Mutation_025265
# Mutation_880324
    with open(KB_FILE, "a") as f: f.write("\n\n# Sync " + datetime.now().isoformat() + "\n" + "\n".join(knowledge))
# Mutation_cce4ff
    with open(SHARE_LOG, "a") as f: json.dump({"timestamp": datetime.now().isoformat(), "entries": len(knowledge)}, f); f.write("\n")
# Mutation_b2ba1f

# Mutation_de93c5
if __name__ == "__main__":
    aggregate_agent_knowledge()
# Mutation_01aa82
# Mutation_a6fff7
    print(f"[{datetime.now()}] ✅ Shared intelligence layer synced.")