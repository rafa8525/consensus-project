import os, datetime, hashlib, json, threading
from pathlib import Path
from typing import Any, Dict

SILENCE = os.getenv("TWILIO_SILENCE", "0").strip() == "1"
ENABLE_SEND = os.getenv("TWILIO_ENABLE_SEND", "0").strip() == "1"
RATE_PER_MIN = int(os.getenv("TWILIO_RATE_PER_MIN", "10"))

LOG_DIR = Path("/home/rafa1215/consensus-project/memory/logs/alerts")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "twilio_blocked.log"
SEND_LOG = LOG_DIR / "twilio_send.log"
STATE_DIR = LOG_DIR / ".state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
RATE_STATE = STATE_DIR / "rate.json"
LOCK = threading.Lock()

def _now_iso() -> str:
    return datetime.datetime.now().isoformat()

def _log(path: Path, msg: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{_now_iso()}] {msg}\n")

def _hash_idempotency(to: str, body: str, template: str = "") -> str:
    h = hashlib.sha256()
    h.update((to or "").encode()); h.update((body or "").encode()); h.update((template or "").encode())
    minute_key = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    h.update(minute_key.encode())
    return h.hexdigest()[:16]

def _rate_ok() -> bool:
    with LOCK:
        minute_key = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        data = {}
        if RATE_STATE.exists():
            try: data = json.loads(RATE_STATE.read_text() or "{}")
            except Exception: data = {}
        if data.get("minute") != minute_key:
            data = {"minute": minute_key, "count": 0}
        if data["count"] >= RATE_PER_MIN:
            return False
        data["count"] += 1
        RATE_STATE.write_text(json.dumps(data))
        return True

def get_status() -> Dict[str, Any]:
    return {
        "silence": SILENCE, "enable_send": ENABLE_SEND, "rate_per_min": RATE_PER_MIN,
        "log_file": str(LOG_FILE), "send_log": str(SEND_LOG)
    }

def send_sms(client, *, to: str, body: str, template: str = "", **kwargs) -> Dict[str, Any]:
    idem = _hash_idempotency(to, body, template)
    if SILENCE:
        _log(LOG_FILE, f"BLOCKED(silence) to={to} idem={idem} body={body[:160]!r} kwargs={{{', '.join(kwargs)}}}")
        return {"status": "blocked", "reason": "silence", "to": to, "idem": idem}
    if not ENABLE_SEND:
        _log(LOG_FILE, f"BLOCKED(enable_flag_missing) to={to} idem={idem} body={body[:160]!r}")
        return {"status": "blocked", "reason": "enable-flag-missing", "to": to, "idem": idem}
    if not _rate_ok():
        _log(LOG_FILE, f"BLOCKED(rate_limit) to={to} idem={idem}")
        return {"status": "blocked", "reason": "rate-limit", "to": to, "idem": idem}
    try:
        msg = getattr(client.messages, "create")(to=to, body=body, **kwargs)
        sid = getattr(msg, "sid", None)
        _log(SEND_LOG, f"SENT to={to} idem={idem} sid={sid} body={body[:160]!r}")
        return {"status": "sent", "to": to, "sid": sid, "idem": idem}
    except Exception as e:
        _log(LOG_FILE, f"ERROR(to={to}, idem={idem}) {type(e).__name__}: {e}")
        raise
