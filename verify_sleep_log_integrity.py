import os
from datetime import datetime
from send_reminder import send_reminder

SLEEP_LOG_DIR = "memory/logs/sleep"
STATUS_LOG = "memory/logs/reminders/sleep_log_verification.txt"
today = datetime.now().strftime("%Y-%m-%d")

# Check for today's sleep log
log_found = False
if os.path.exists(SLEEP_LOG_DIR):
    for f in os.listdir(SLEEP_LOG_DIR):
        path = os.path.join(SLEEP_LOG_DIR, f)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
            if mtime == today:
                log_found = True
                break

# Handle result
if log_found:
    status = f"{today} - ✅ Sleep log exists"
else:
    status = f"{today} - ⚠️ No sleep log found"
    try:
        send_reminder("ALERT: No sleep log detected for today.")
    except Exception as e:
        with open(STATUS_LOG, "a") as f:
            f.write(f"{datetime.now()} - ❌ SMS alert failed: {e}\n")

with open(STATUS_LOG, "a") as f:
    f.write(status + "\n")

print(status)