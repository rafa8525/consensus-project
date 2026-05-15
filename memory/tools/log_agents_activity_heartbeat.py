from datetime import datetime
import os

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Path to agents folder
base_dir = "/home/rafa1215/memory/logs/agents"
ensure_directory_exists(base_dir)

# Today's date
today = datetime.now().strftime("%Y-%m-%d")

# Target files
files = {
    f"agents_log.md": f"# Agent Task Log – {today}\n\nAll agent activity for {today} is recorded here.\n",
    f"knowledge_shared_{today}.md": f"# Knowledge Shared – {today}\n\nShared insights, patterns, and critical updates from agents.\n",
    f"lessons_learned_{today}.md": f"# Lessons Learned – {today}\n\nCaptured observations from agent behavior, edge cases, and failures.\n",
    f"simulations_{today}.md": f"# Simulation Log – {today}\n\nSimulation-driven evaluations for agent decision-making on {today}.\n"
}

# Write each file
for name, content in files.items():
    full_path = os.path.join(base_dir, name)
    with open(full_path, "w") as f:
        f.write(content)
