#!/usr/bin/env python3
"""
Append a successful absorb event to the JSONL history and update state.

Usage:
  python3 tools/absorb_log_append.py [am|pm]
  or: TARGET_WINDOW=am|pm python3 tools/absorb_log_append.py
  Optional: ABSORB_TS_ISO=<iso8601> to override timestamp
"""
import os, sys, json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
LOG_PATH = Path("memory/logs/absorb/absorb_success_log.jsonl")
STATE_PATH = Path("memory/logs/absorb/absorb_state.json")
def ensure_dirs():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def choose_window(argv) -> str:
    if len(argv) >= 2 and argv[1] in ("am","pm"):
        return argv[1]
    env = os.environ.get("TARGET_WINDOW","").lower()
    if env in ("am","pm"):
        return env
    return "pm"

def choose_timestamp() -> str:
    ts_env = os.environ.get("ABSORB_TS_ISO","").strip()
    if ts_env:
        try:
            datetime.fromisoformat(ts_env)
            return ts_env
        except Exception:
            pass
    return datetime.now(TZ).isoformat()
def append_history(ts_iso: str, window: str) -> None:
    entry = {"ts": ts_iso, "window": window}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def update_state(ts_iso: str, window: str) -> None:
    state = {}
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8") or "{}")
        except Exception:
            state = {}
    state["last_attempt"] = ts_iso
    if window == "am":
        state["last_am_success"] = ts_iso
    else:
        state["last_pm_success"] = ts_iso
    state["last_error"] = ""
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
def main(argv):
    ensure_dirs()
    window = choose_window(argv)
    ts_iso = choose_timestamp()
    append_history(ts_iso, window)
    update_state(ts_iso, window)
    print(f"Appended {window} success @ {ts_iso}")

if __name__ == "__main__":
    main(sys.argv)
