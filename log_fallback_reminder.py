import datetime
from pathlib import Path

def log_fallback_reminder(reason, context):
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/reminders")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"fallback_log_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()

    entry = f"{timestamp} — ⚠️ Reminder failed — Reason: {reason} — Context: {context}\n"

    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example: SMS failure
    log_fallback_reminder("Twilio HTTP 401", "send_sms_reminder() call failed")
