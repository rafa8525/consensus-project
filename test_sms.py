#!/usr/bin/env python3
"""
test_sms.py
Purpose: Standalone test harness for twilio_guard.send_sms
Safe: No console closure, logs both to stdout and project log file
"""

import datetime
from pathlib import Path
from twilio_guard import send_sms

# Config
TO_NUMBER = "+16502283267"
LOG_FILE = Path("/home/rafa1215/consensus-project/memory/logs/system/sms_test.md")

def log(line: str):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")
    print(f"[{ts}] {line}")

def main():
    body = "✅ Test SMS from twilio_guard test script"
    try:
        result = send_sms(to=TO_NUMBER, body=body)
        log(f"SUCCESS: SMS sent to {TO_NUMBER}. Result: {result}")
    except Exception as e:
        log(f"ERROR: Failed to send SMS to {TO_NUMBER}. Error: {e}")

if __name__ == "__main__":
    main()
