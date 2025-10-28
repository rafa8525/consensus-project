#!/usr/bin/env python3
from pathlib import Path
import datetime

root = Path.home() / "consensus-project" / "memory" / "logs" / "system"
root.mkdir(parents=True, exist_ok=True)
manifest_file = root / "daily_agent_task_manifest.md"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

content = [
    "# Daily Agent Task Manifest",
    f"**Generated:** {timestamp}",
    "---",
    "Each agent listed here must:",
    "1. Perform at least one improvement task daily.",
    "2. If no internal improvement exists, research external AI agents publicly available online and adapt beneficial methods.",
    "3. Log findings or actions in `/memory/logs/agents/<agent>/`.",
    "---\n"
]

agents_dir = Path.home() / "consensus-project" / "memory" / "logs" / "docs" / "auto_generated"
agents = sorted([p.stem for p in agents_dir.glob("*_summary_*.md")])

for a in agents:
    display_name = a.replace("_summary", "").replace("_", " ").title()
    section = (
        f"## {display_name}\n"
        f"- **Status:** ✅ Active\n"
        f"- **Daily Directive:** Improve the project or research external methods.\n"
        f"- **Last Check-In:** {timestamp}\n---\n"
    )
    content.append(section)

manifest_file.write_text("\n".join(content))
print(f"✅ Daily manifest generated with {len(agents)} agents → {manifest_file}")
