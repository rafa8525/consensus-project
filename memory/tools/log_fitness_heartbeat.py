# log_fitness_heartbeat.py
from datetime import datetime
import os

# Define log directory and ensure it exists
log_dir = "/home/rafa1215/consensus-project/memory/logs/fitness"
os.makedirs(log_dir, exist_ok=True)

# Format today's date
today = datetime.now().strftime("%Y-%m-%d")
filename = f"heartbeat_{today}.md"
filepath = os.path.join(log_dir, filename)

# Message to write
timestamp = datetime.now().isoformat()
content = f"""## ✅ Fitness Heartbeat Log — {today}

- Timestamp: {timestamp}
- Daily Summary: No activity logs auto-detected.
- Status: Heartbeat recorded to confirm log integrity.

If this entry is empty, something went wrong or no data was logged today.
"""

# Only write if file doesn't exist
if not os.path.exists(filepath):
    with open(filepath, "w") as f:
        f.write(content)
    print(f"[✔] Fitness heartbeat created: {filepath}")
else:
    print(f"[↪] Fitness heartbeat already exists: {filepath}")
