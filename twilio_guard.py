#!/usr/bin/env python3
"""
twilio_guard.py
Central SMS send guard for PythonAnywhere consensus project.

Features:
- Kill switch via env (TWILIO_SILENCE=1 or TWILIO_ENABLE_SEND != 1)
- Quiet hours enforcement (default 22:00–08:00 local time)
- Rate limiting (per-minute cap, default 10/min)
- Global deduplication across processes (24h cache file)
- Escalation handling: quiet-hour messages queued & sent after hours
- Structured logging (success, blocked, queued)
"""

import os
import sys
import time
import json
import hashlib
import datetime
import threading
from pathlib import Path
from twilio.rest import Client

# ===== CONFIG =====
PROJECT_ROOT = Path("/home/rafa1215/consensus-project")
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
STATE_FILE = LOG_DIR / "twilio_guard_state.json"
SEND_LOG = LOG_DIR / "twilio_send.md"
BLOCK_LOG = LOG_DIR / "twilio_block.md"
QUEUE_FILE = LOG_DIR / "twilio_queue.json"

QUIET_START = 22  # 10 PM
QUIET_END = 8     # 8 AM
RATE_PER_MIN = 10
DEDUP_HOURS = 24

# ===== TWILIO SETUP =====
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "")

client = None
if TWILIO_SID and TWILIO_AUTH:
    client = Client(TWILIO_SID, TWILIO_AUTH)

lock = threading.Lock()


def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def is_quiet_hours():
    """Return True if current local hour is within quiet hours."""
    now = datetime.datetime.now()
    if QUIET_START < QUIET_END:
        return QUIET_START <= now.hour < QUIET_END
    else:  # handles windows that cross midnight
        return now.hour >= QUIET_START or now.hour < QUIET_END


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def log_md(path, line):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{now_iso()}] {line}\n")


def idem_key(to, body, template=None):
    h = hashlib.sha256()
    h.update((to + (body or "") + (template or "")).encode("utf-8"))
    return h.hexdigest()


def should_block(to, body, template=None):
    """Apply kill switch, quiet hours, rate limit, and dedup rules."""
    # Kill switches
    if os.getenv("TWILIO_SILENCE") == "1":
        return "silenced"
    if os.getenv("TWILIO_ENABLE_SEND") != "1":
        return "disabled"

    state = load_state()
    now = datetime.datetime.utcnow()
    minute_key = now.strftime("%Y%m%d%H%M")

    # Quiet hours: log & queue instead of send
    if is_quiet_hours():
        queue_message(to, body, template)
        return "quiet_hours"

    # Rate limiting
    minute_count = state.get("minute_counts", {}).get(minute_key, 0)
    if minute_count >= RATE_PER_MIN:
        return "rate_limited"

    # Deduplication
    key = idem_key(to, body, template)
    history = state.get("history", {})
    cutoff = (now - datetime.timedelta(hours=DEDUP_HOURS)).isoformat()
    for k, ts in list(history.items()):
        if ts < cutoff:
            history.pop(k, None)
    if key in history:
        return "duplicate"

    # Passed all checks, record usage
    state.setdefault("minute_counts", {})[minute_key] = minute_count + 1
    state.setdefault("history", {})[key] = now.isoformat()
    save_state(state)
    return None


def queue_message(to, body, template=None):
    """Store quiet-hour messages for later delivery."""
    q = []
    if QUEUE_FILE.exists():
        try:
            q = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception:
            q = []
    q.append({
        "to": to,
        "body": body,
        "template": template,
        "queued_at": now_iso(),
    })
    QUEUE_FILE.write_text(json.dumps(q, indent=2), encoding="utf-8")
    log_md(BLOCK_LOG, f"Queued (quiet hours) → {to}: {body[:80]}")


def flush_queue():
    """Send queued messages if quiet hours are over."""
    if not QUEUE_FILE.exists():
        return
    try:
        q = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return
    if not q:
        return
    if is_quiet_hours():
        return
    QUEUE_FILE.unlink(missing_ok=True)
    for msg in q:
        send_sms(msg["to"], msg["body"], msg.get("template"), bypass_queue=True)


def send_sms(to, body, template=None, bypass_queue=False):
    """
    Main entrypoint: guarded SMS send.
    Returns dict {status, sid?, error?}
    """
    with lock:
        if not bypass_queue:
            flush_queue()

        reason = should_block(to, body, template)
        if reason:
            log_md(BLOCK_LOG, f"Blocked ({reason}) → {to}: {body[:80]}")
            return {"status": "blocked", "reason": reason}

        if not client:
            log_md(BLOCK_LOG, f"Blocked (no Twilio client) → {to}: {body[:80]}")
            return {"status": "blocked", "reason": "no_client"}

        try:
            msg = client.messages.create(
                to=to,
                from_=TWILIO_FROM,
                body=body
            )
            log_md(SEND_LOG, f"Sent → {to} sid={msg.sid} body={body[:80]}")
            return {"status": "sent", "sid": msg.sid}
        except Exception as e:
            log_md(BLOCK_LOG, f"Error sending → {to}: {e}")
            return {"status": "error", "error": str(e)}
