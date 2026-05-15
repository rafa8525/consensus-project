#!/usr/bin/env python3
import os
import pytz
from datetime import datetime
import subprocess
import logging

# ==============================
# CONFIGURATION
# ==============================
TIMEZONE = pytz.timezone("America/Los_Angeles")
SEND_WINDOW_START = 9   # 9 AM PDT
SEND_WINDOW_END = 16    # 4 PM PDT
HEARTBEAT_LOG = "/home/rafa1215/memory/logs/agents/reminder_heartbeat.log"
GITHUB_LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/agents/reminder_block_log.md"

# Commands for sending reminders (SMS & voice)
SMS_COMMAND = ["python3", "/home/rafa1215/memory/tools/send_sms_reminder.py"]
VOICE_COMMAND = ["python3", "/home/rafa1215/memory/tools/dispatch_voice_reminders.py"]

# Git commands for auto-pushing logs
GIT_ADD = ["git", "-C", "/home/rafa1215/consensus-project", "add", "."]
GIT_COMMIT = [
    "git", "-C", "/home/rafa1215/consensus-project",
    "commit", "-m", "Auto-log: reminder blocked outside allowed window"
]
GIT_PUSH = ["git", "-C", "/home/rafa1215/consensus-project", "push"]

# ==============================
# LOGGING SETUP
# ==============================
logging.basicConfig(
    filename=HEARTBEAT_LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# FUNCTION: Check if current time is within allowed window
# ==============================
def within_allowed_window():
    now = datetime.now(TIMEZONE)
    return SEND_WINDOW_START <= now.hour < SEND_WINDOW_END

# ==============================
# FUNCTION: Send reminders
# ==============================
def send_reminders():
    try:
        subprocess.run(SMS_COMMAND, check=True)
        logging.info("SMS reminder sent successfully.")

        subprocess.run(VOICE_COMMAND, check=True)
        logging.info("Voice reminder sent successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Reminder sending failed: {e}")

# ==============================
# FUNCTION: Log block to GitHub
# ==============================
def log_block_to_github():
    now = datetime.now(TIMEZONE)
    log_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S %Z')} - Reminder blocked outside allowed window\n"

    # Append to GitHub log file
    with open(GITHUB_LOG_FILE, "a") as f:
        f.write(log_entry)

    # Push to GitHub
    try:
        subprocess.run(GIT_ADD, check=True)
        subprocess.run(GIT_COMMIT, check=True)
        subprocess.run(GIT_PUSH, check=True)
        logging.info("Blocked reminder logged to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to push blocked reminder log to GitHub: {e}")

# ==============================
# MAIN EXECUTION
# ==============================
if __name__ == "__main__":
    if within_allowed_window():
        send_reminders()
    else:
        now = datetime.now(TIMEZONE)
        logging.warning(
            f"Reminder blocked - Attempt outside allowed window ({now.strftime('%H:%M %Z')})"
        )
        log_block_to_github()
