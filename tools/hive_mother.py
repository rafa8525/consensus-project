#!/usr/bin/env python3
"""
Hive Mother Agent – Final Stable Daily Version
----------------------------------------------
Purpose:
  • Runs hourly (for monitoring) but emails once per day at 07:00 AM PST (15 UTC)
  • Prevents multiple emails for the same date
  • Logs every check to ~/memory/logs/system/hive_mother.log
"""

import os
import json
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
import random
import sys

# === Configuration ===
LOG_PATH = os.path.expanduser("~/memory/logs/system/hive_mother.log")
ALERT_STATE = os.path.expanduser("~/memory/logs/system/hive_mother_alerts.json")
CONF_THRESHOLD = 50.0        # below this → "low confidence"
DAILY_SEND_HOUR_UTC = 15     # 07:00 AM PST
FROM_EMAIL = "rafa8525@gmail.com"
TO_EMAIL = "rafa8525@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # set via .env or env vars

# === Utilities ===
def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def load_state() -> dict:
    if not os.path.exists(ALERT_STATE):
        return {}
    try:
        with open(ALERT_STATE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict):
    os.makedirs(os.path.dirname(ALERT_STATE), exist_ok=True)
    with open(ALERT_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f)

def get_confidence() -> float:
    # Replace with real metric if available
    return round(random.uniform(40.0, 70.0), 2)

def send_email(confidence: float):
    subject = f"⚠️ Hive Mother Alert — Low Predictive Confidence ({confidence:.2f}%)"
    body = (
        f"Triggered at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Predictive Confidence: {confidence:.2f}%\n"
        f"Threshold: {CONF_THRESHOLD:.2f}%\n\n"
        "This is the only Hive Mother email for today."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        log(f"📧 Email sent successfully — {subject}")
    except Exception as e:
        log(f"❌ Email failed: {e}")

# === Main ===
def main():
    now = datetime.now(timezone.utc)
    confidence = get_confidence()
    log(f"Checked predictive confidence: {confidence:.2f}%")

    # Read state and ensure only one daily send
    state = load_state()
    today = now.strftime("%Y-%m-%d")
    if state.get("last_sent_date") == today:
        log("Daily alert already sent — no email needed.")
        return

    if confidence < CONF_THRESHOLD and now.hour == DAILY_SEND_HOUR_UTC:
        send_email(confidence)
        state["last_sent_date"] = today
        save_state(state)
    else:
        log("Confidence normal or not time to send.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Unhandled error: {e}")
        sys.exit(1)
