#!/usr/bin/env python3
from common import twilio_guard
# -*- coding: utf-8 -*-
"""
AI Consensus System – SMS Persistence Daemon
Author: Rafael / AI Consensus System
Purpose: Ensure Twilio SMS delivery continues when ChatGPT or Flask session is inactive.
"""

import os
import json
import time
import traceback
from datetime import datetime, timezone
from twilio.rest import Client

# ---------------- Configuration ---------------- #
BASE_DIR = os.path.expanduser("~/consensus-project")
QUEUE_DIR = os.path.join(BASE_DIR, "memory/queue/reminders")
LOG_DIR = os.path.join(BASE_DIR, "memory/logs/system/sms_daemon")
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Pull credentials from environment for security
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TO_NUMBER = os.getenv("TWILIO_TO")
FROM_NUMBER = os.getenv("TWILIO_FROM")

CHECK_INTERVAL = 300  # seconds (5 min)
QUIET_HOURS = (22, 7)  # no SMS between 10 PM – 7 AM local time


def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message):
    log_file = os.path.join(LOG_DIR, f"sms_persistence_{datetime.now(timezone.utc).date()}.log")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp()}] {message}\n")
    print(message)


def quiet_hours_now():
    """Check if current local time falls in quiet hours."""
    local_hour = datetime.now().hour
    start, end = QUIET_HOURS
    if start < end:
        return start <= local_hour < end
    return local_hour >= start or local_hour < end


def send_sms_via_twilio(body: str):
    if not all([ACCOUNT_SID, AUTH_TOKEN, TO_NUMBER, FROM_NUMBER]):
        log("❌ Missing Twilio credentials — cannot send SMS.")
        return False
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        msg = clienttwilio_guard.send_sms(client, body=body, from_=FROM_NUMBER, to=TO_NUMBER)
        log(f"✅ SMS sent (SID: {msg.sid}) | Body: {body}")
        return True
    except Exception as e:
        log(f"❌ SMS send failure: {e}")
        return False


def process_queue():
    """Send pending reminders from the queue folder."""
    for file in os.listdir(QUEUE_DIR):
        if not file.endswith(".json"):
            continue
        fpath = os.path.join(QUEUE_DIR, file)
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
            body = data.get("message", "No message body")
            created = data.get("created_at", "unknown time")

            if quiet_hours_now():
                log(f"⏸ Quiet hours active. Deferring message created at {created}.")
                continue

            if send_sms_via_twilio(body):
                os.remove(fpath)
                log(f"🗑 Removed delivered reminder: {file}")
            else:
                log(f"⚠️ Failed to send reminder: {file}")

        except Exception:
            log(f"❌ Error processing file {file}\n{traceback.format_exc()}")


def main():
    log("=== SMS Persistence Daemon Started ===")
    while True:
        try:
            process_queue()
            log("💤 Idle... Next check in 5 min.")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log("🛑 SMS Persistence Daemon stopped manually.")
            break
        except Exception:
            log(traceback.format_exc())
            time.sleep(10)


if __name__ == "__main__":
    main()