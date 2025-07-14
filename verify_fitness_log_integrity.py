import os
from datetime import datetime
from send_reminder import send_reminder

FITNESS_LOG_DIR = "memory/logs/fitness"
STATUS_LOG = "memory/logs/reminders/fitness_log_verification.txt"
today = datetime.now().strftime("%Y-%m-%d")

# Scan for any file modified today in the fitness log directory
log_found = False
if os.path.exists(FITNESS_LOG_DIR):
    for f in os.listdir(FITNESS_LOG_DIR):
        path = os.path.join(FITNESS_LOG_DIR, f)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
            if mtime == today:
                log_found = True
                break

# Record and act
if log_found:
    status = f"{today} - ✅ Fitness log exists"
else:
    status = f"{today} - ⚠️ No fitness log found"
    try:
        send_reminder("ALERT: No fitness data logged today.")
    except Exception as e:
        with open(STATUS_LOG, "a") as f:
            f.write(f"{datetime.now()} - ❌ SMS alert failed: {e}\n")

with open(STATUS_LOG, "a") as f:
    f.write(status + "\n")

print(status)