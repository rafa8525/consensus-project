import os
from datetime import datetime
from send_reminder import send_reminder

NUTRITION_LOG_DIR = "memory/logs/nutrition"
STATUS_LOG = "memory/logs/reminders/nutrition_log_verification.txt"
today = datetime.now().strftime("%Y-%m-%d")

# Look for today’s log
log_found = False
if os.path.exists(NUTRITION_LOG_DIR):
    for f in os.listdir(NUTRITION_LOG_DIR):
        path = os.path.join(NUTRITION_LOG_DIR, f)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
            if mtime == today:
                log_found = True
                break

if log_found:
    status = f"{today} - ✅ Nutrition log exists"
else:
    status = f"{today} - ⚠️ No nutrition log found"
    try:
        send_reminder("ALERT: No nutrition log entry detected today.")
    except Exception as e:
        with open(STATUS_LOG, "a") as f:
            f.write(f"{datetime.now()} - ❌ SMS alert failed: {e}\n")

with open(STATUS_LOG, "a") as f:
    f.write(status + "\n")

print(status)