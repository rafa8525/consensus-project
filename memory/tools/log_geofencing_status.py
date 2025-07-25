# log_geofencing_status.py

from datetime import datetime
import os

log_dir = "/home/rafa1215/consensus-project/memory/logs/project-updates/"
log_file = os.path.join(log_dir, f"geofencing_status_{datetime.now().strftime('%Y-%m-%d')}.md")

os.makedirs(log_dir, exist_ok=True)

content = f"""\
# Geofencing Automation and Heartbeat Logging

- Date: {datetime.now().strftime('%Y-%m-%d')}
- Kitchen zone: logging active
- Cron task: scheduled and visible in PythonAnywhere
- Status: On track — heartbeat confirmed
- Next: Pool and Store detection setup, fallback if logs go silent
"""

with open(log_file, "w") as f:
    f.write(content)

print(f"[✔] Geofencing project update log written to {log_file}")
