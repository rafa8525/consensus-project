#!/usr/bin/env python3
from pathlib import Path
import datetime

root = Path.home()/ "consensus-project"/"memory"/"logs"/"docs"/"auto_generated"
root.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

agents = [
    # Phase 1
    "Project Manager Agent","Enhancement Tracker Agent","Fitness Agent","VPN Control Agent",
    "Security Audit Agent","Geofence Agent","Financial Log Agent","Daily Summary Agent",
    "Movie Recommender Agent","Backup and Sync Agent",
    # Phase 2
    "Memory Refactorer Agent","Prompt Optimizer Agent","Behavioral Nudger Agent",
    "Meal Quality Analyzer Agent","Offline Mode Agent","Pattern Spotter Agent",
    "Consensus Ranking Agent","Log Keeper Agent","Task Consolidator Agent",
    "External Learner Agent","Quality Control Agent"
]

for a in agents:
    slug=a.lower().replace(" ","_")
    f=root/f"{slug}_summary_{ts}.md"
    f.write_text(f"# {a}\n**Generated:** {datetime.datetime.now().isoformat()}\n**Status:** ✅ Active\n\n---\n")
print(f"✅ Generated {len(agents)} docs → {root}")
