import os
from datetime import datetime
from send_reminder import send_reminder

SMS_LOG_PATH = "memory/logs/reminders/fallback_log.txt"
STATUS_LOG = "memory/logs/reminders/sms_log_verification.txt"
today = datetime.now().strftime("%Y-%m-%d")

log_found = False
if os.path.exists(SMS_LOG_PATH):
    with open(SMS_LOG_PATH, "r") as f:
        for line in f:
            if line.startswith(today):
                log_found = True
                break

if log_found:
    status = f"{today} - ✅ SMS fallback log exists"
else:
    status = f"{today} - ⚠️ No SMS fallback log found"
    try:
        send_reminder("ALERT: No SMS fallback log found today.")
    except Exception as e:
        with open(STATUS_LOG, "a") as f:
            f.write(f"{datetime.now()} - ❌ SMS alert failed: {e}\n")

with open(STATUS_LOG, "a") as f:
    f.write(status + "\n")

print(status)