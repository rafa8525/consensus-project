#!/usr/bin/env python3
from common import twilio_guard
# twilio_guard.py
# Purpose: Controlled Twilio SMS sender with quiet hours, whitelist, and rate limits.
# Safe defaults: no emoji, no console-closing side effects.

import os
import sys
import time
import logging
import datetime
from pathlib import Path
from collections import defaultdict
from twilio.rest import Client

# --- Paths ---
PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
LOG_FILE = PROJECT_ROOT / "memory" / "logs" / "system" / "twilio_guard.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Load env ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "").strip()

SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
SMS_WHITELIST = [n.strip() for n in os.getenv("SMS_WHITELIST", "").split(",") if n.strip()]
SMS_QUIET_HOURS = os.getenv("SMS_QUIET_HOURS", "21-08")
SMS_MAX_PER_HOUR = int(os.getenv("SMS_MAX_PER_HOUR", "1"))
SMS_MAX_PER_DAY = int(os.getenv("SMS_MAX_PER_DAY", "2"))

# --- State for rate limiting ---
sent_log = defaultdict(list)  # {number: [timestamps]}

def within_quiet_hours():
    """Return True if current UTC time is within quiet hours."""
    try:
        start, end = SMS_QUIET_HOURS.split("-")
        start_h, end_h = int(start), int(end)
        now_h = datetime.datetime.utcnow().hour
        if start_h < end_h:
            return start_h <= now_h < end_h
        else:
            # overnight range (e.g., 21-08)
            return now_h >= start_h or now_h < end_h
    except Exception:
        return False

def rate_limit_check(to_number: str) -> tuple[bool, str]:
    """Check per-hour and per-day limits."""
    now = time.time()
    one_hour = 3600
    one_day = 86400

    # Filter old timestamps
    sent_log[to_number] = [t for t in sent_log[to_number] if now - t < one_day]

    # Hourly check
    if sum(1 for t in sent_log[to_number] if now - t < one_hour) >= SMS_MAX_PER_HOUR:
        return False, "hourly limit reached"

    # Daily check
    if len(sent_log[to_number]) >= SMS_MAX_PER_DAY:
        return False, "daily limit reached"

    return True, "ok"

def send_sms(to: str, body: str):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    if not SMS_ENABLED:
        logging.warning(f"[{ts}] SMS disabled by config. To={to} Body={body[:40]}")
        return {"status": "disabled"}

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_FROM_NUMBER:
        logging.error(f"[{ts}] Missing Twilio credentials. Cannot send SMS.")
        return {"status": "error", "reason": "missing_credentials"}

    if SMS_WHITELIST and to not in SMS_WHITELIST:
        logging.warning(f"[{ts}] Blocked: {to} not in whitelist")
        return {"status": "blocked", "reason": "not_whitelisted"}

    if within_quiet_hours():
        logging.warning(f"[{ts}] Blocked: quiet hours. To={to}")
        return {"status": "blocked", "reason": "quiet_hours"}

    ok, reason = rate_limit_check(to)
    if not ok:
        logging.warning(f"[{ts}] Blocked: {reason}. To={to}")
        return {"status": "blocked", "reason": reason}

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = clienttwilio_guard.send_sms(client, 
            body=body,
            from_=TWILIO_FROM_NUMBER,
            to=to
        )
        sent_log[to].append(time.time())
        logging.info(f"[{ts}] SMS sent. To={to} SID={msg.sid}")
        return {"status": "success", "sid": msg.sid}
    except Exception as e:
        logging.error(f"[{ts}] SMS send failed: {e}")
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    # Example standalone usage
    result = send_sms(os.getenv("SMS_TO_NUMBER", "+16502283267"), "Test message from twilio_guard.py")
    print(result)