#!/usr/bin/env python3
"""
twilio_guard.py
Centralized SMS Dispatcher for Consensus Project

Features:
- Reads Twilio credentials from .env
- Enforces quiet hours (default: 22:00–07:00)
- Enforces daily rate limits (default: 3 SMS, 1 call)
- Deduplicates repeated messages (same body within 1 hour)
- Logs all activity to memory/logs/system/twilio_guard.log
- Provides send_sms() API for other agents to call

Platform: PythonAnywhere-safe. No emojis. No console-closing effects.
"""

import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

# === CONFIG ===
PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
STATE_FILE = LOG_DIR / "twilio_guard_state.json"

QUIET_HOURS = (22, 7)  # No SMS between 22:00–07:00
MAX_SMS_PER_DAY = 3
DEDUP_WINDOW_SEC = 3600  # 1 hour

# === Setup logging ===
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "twilio_guard.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# === Load credentials ===
load_dotenv(PROJECT_ROOT / ".env")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER]):
    logging.error("Missing Twilio credentials in .env")
    sys.exit(1)

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def within_quiet_hours(now):
    """Return True if current time is within quiet hours."""
    h = now.hour
    start, end = QUIET_HOURS
    if start < end:
        return start <= h < end
    else:
        return h >= start or h < end


def send_sms(to: str, body: str):
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date().isoformat()
    state = load_state()

    # Daily counters
    counters = state.get("daily", {})
    if counters.get("date") != today:
        counters = {"date": today, "sms_count": 0, "last_messages": []}

    # Quiet hours check
    if within_quiet_hours(now):
        msg = f"Blocked (quiet hours): {body[:60]}..."
        logging.warning(msg)
        return {"status": "blocked", "reason": "quiet_hours"}

    # Rate limit check
    if counters["sms_count"] >= MAX_SMS_PER_DAY:
        msg = f"Blocked (daily limit reached): {body[:60]}..."
        logging.warning(msg)
        return {"status": "blocked", "reason": "daily_limit"}

    # Deduplication check
    recent = counters["last_messages"]
    for entry in recent:
        if (
            entry["body"] == body
            and (now.timestamp() - entry["ts"]) < DEDUP_WINDOW_SEC
        ):
            logging.warning(f"Blocked (duplicate): {body[:60]}...")
            return {"status": "blocked", "reason": "duplicate"}

    # Attempt send
    try:
        msg = client.messages.create(
            to=to, from_=FROM_NUMBER, body=body
        )
        logging.info(f"SMS sent to {to}: {body[:60]}...")
        counters["sms_count"] += 1
        recent.append({"body": body, "ts": now.timestamp()})
        recent = [m for m in recent if now.timestamp() - m["ts"] < DEDUP_WINDOW_SEC]
        counters["last_messages"] = recent
        state["daily"] = counters
        save_state(state)
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        logging.error(f"SMS send failed: {e}")
        return {"status": "failed", "reason": str(e)}


if __name__ == "__main__":
    # Example manual test
    res = send_sms(to="+16502283267", body="Twilio Guard test message")
    print(res)
