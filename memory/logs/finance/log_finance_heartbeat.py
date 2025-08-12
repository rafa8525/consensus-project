# /home/rafa1215/memory/tools/log_finance_heartbeat.py

import os
from datetime import datetime

# Prepare path and filename
today = datetime.now().strftime('%Y-%m-%d')
folder_path = "/home/rafa1215/memory/logs/finance"
os.makedirs(folder_path, exist_ok=True)

log_file = os.path.join(folder_path, f"{today}_finance_log.md")

# Log contents
log_data = f"""# Finance Log — {today}

This file confirms heartbeat logging is active for the finance folder.
Timestamp: {datetime.now().isoformat()}

- [ ] Log at least one new finance entry this week.
- [ ] Check ride-share savings and bill payment reminders.
"""

# Write to file
with open(log_file, "w") as f:
    f.write(log_data)

print(f"[✔] Finance log created: {log_file}")
