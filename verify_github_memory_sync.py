import os
from datetime import datetime
from send_reminder import send_reminder

LOG_PATH = "memory/logs/reminders/github_memory_check_log.txt"
STATUS_LOG = "memory/logs/reminders/github_memory_check_verification.txt"

today = datetime.now().strftime("%Y-%m-%d")
count = 0

# Count today's sync logs
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        for line in f:
            if line.startswith(today):
                count += 1

# Log status
if count >= 4:
    status = f"{today} - ✅ All 4 memory syncs completed"
else:
    status = f"{today} - ⚠️ Only {count} of 4 memory syncs detected — investigate"
    try:
        send_reminder(f"ALERT: Only {count} of 4 GitHub memory syncs completed today.")
    except Exception as e:
        with open(STATUS_LOG, "a") as f:
            f.write(f"{datetime.now()} - ❌ SMS alert failed: {e}\n")

with open(STATUS_LOG, "a") as f:
    f.write(status + "\n")

print(status)