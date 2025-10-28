#!/usr/bin/env python3
from pathlib import Path
import datetime

root = Path.home()/ "consensus-project"/"memory"/"logs"/"docs"/"auto_generated"
root.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

agents = [
    # Phase 5
    "Scenario Simulator Agent","Quality Control Auditor Agent","Redundancy Checker Agent",
    "Meta-Learning Refiner Agent","Consensus Evaluator Agent",
    # Phase 6
    "Pool Reminder Agent","Weather-Based Fitness Agent","Voice-Trigger Agent",
    "SMS Notification Agent","Finance Monitor Agent","GitHub Visibility Agent",
    "Cleanup Agent","Simulation Supervisor Agent","Absorption Monitor Agent",
    "System Health Evaluator Agent"
]

for a in agents:
    slug=a.lower().replace(" ","_")
    f=root/f"{slug}_summary_{ts}.md"
    f.write_text(f"# {a}\n**Generated:** {datetime.datetime.now().isoformat()}\n**Status:** ✅ Active\n\n---\n")
print(f"✅ Generated {len(agents)} docs → {root}")
