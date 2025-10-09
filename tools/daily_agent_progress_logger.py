cat > /home/rafa1215/consensus-project/tools/daily_agent_progress_logger.py <<'PY'
#!/usr/bin/env python3
from pathlib import Path
import datetime

# Paths
root = Path.home() / "consensus-project" / "memory" / "logs" / "system"
root.mkdir(parents=True, exist_ok=True)
today = datetime.date.today().strftime("%Y-%m-%d")
log_file = root / f"daily_agent_progress_{today}.md"

# Header
ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
content = [
    f"# Daily Agent Progress Log — {today}",
    f"**Generated:** {ts}",
    "---",
    "Each entry reflects what the agent improved today or, if no internal task was pending, any external research performed.\n"
]

# Discover all active agent docs
agents_dir = Path.home() / "consensus-project" / "memory" / "logs" / "docs" / "auto_generated"
agents = sorted([p.stem for p in agents_dir.glob("*_summary_*.md")])

# Build simple default entries
for a in agents:
    display = a.replace("_summary", "").replace("_", " ").title()
    section = (
        f"## {display}\n"
        f"- **Status:** ✅ Active\n"
        f"- **Activity:** (auto-logged placeholder — agent will append details)\n"
        f"- **Timestamp:** {ts}\n---\n"
    )
    content.append(section)

# Write the file
log_file.write_text("\n".join(content))
print(f"✅ Created daily progress log for {len(agents)} agents → {log_file}")
PY

chmod +x /home/rafa1215/consensus-project/tools/daily_agent_progress_logger.py
