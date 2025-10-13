# shared_intelligence_loop.py
from datetime import datetime
from pathlib import Path
import json, glob

BASE = Path("/home/rafa1215/consensus-project/memory")
KB_FILE = BASE / "centralized_knowledge_base.txt"
SHARE_LOG = BASE / "logs/system/shared_insights.json"

def aggregate_agent_knowledge():
    knowledge = []
    for file in glob.glob(str(BASE / "logs/agent_summaries/*.md")):
        with open(file) as f: knowledge.append(f.read())
    with open(KB_FILE, "a") as f: f.write("\n\n# Sync " + datetime.now().isoformat() + "\n" + "\n".join(knowledge))
    with open(SHARE_LOG, "a") as f: json.dump({"timestamp": datetime.now().isoformat(), "entries": len(knowledge)}, f); f.write("\n")

if __name__ == "__main__":
    aggregate_agent_knowledge()
    print(f"[{datetime.now()}] ✅ Shared intelligence layer synced.")
