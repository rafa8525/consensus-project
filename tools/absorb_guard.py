#!/usr/bin/env python3
"""
Absorb Guard (DST-safe, with grace period)

What this does
--------------
- Checks AM/PM absorb windows in America/Los_Angeles time.
- If a window has PASSED and there's no "ok" log for that window today,
  it triggers a catch-up run via tools/absorb_runner.py.
- Adds a small grace period after each window end to avoid racing the scheduler.
- Prints clear actions to stdout for easy PythonAnywhere job logs.

Config (optional via env)
-------------------------
ABSORB_GUARD_GRACE_MIN   : minutes after window end to wait before catch-up (default: 5)
ABSORB_WINDOW_AM         : "HH:MM-HH:MM" for AM window (default: "08:00-12:00")
ABSORB_WINDOW_PM         : "HH:MM-HH:MM" for PM window (default: "14:00-18:00")
"""

import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

LOG_FILE = Path("memory/logs/absorb/absorb_log.jsonl")

# --- Timezone handling (DST-safe) ---
def _make_now_pt():
    """Return timezone-aware now() in America/Los_Angeles; fallback if zoneinfo unavailable."""
    try:
        from zoneinfo import ZoneInfo
        PT = ZoneInfo("America/Los_Angeles")
        return lambda: datetime.now(PT)
    except Exception:
        # Fallback: compute PT from UTC; adjust offset seasonally if desired.
        # Uses timezone-aware UTC to avoid deprecation warnings.
        # Default to PDT (-7). If you need PST in winter on fallback, adjust here.
        PT_OFFSET = -7
        def _now_pt_fallback():
            return datetime.now(timezone.utc) + timedelta(hours=PT_OFFSET)
        return _now_pt_fallback

now_pt = _make_now_pt()

# --- Window configuration ---
def _parse_window(s: str):
    # "HH:MM-HH:MM" -> ((h1,m1),(h2,m2))
    a, b = s.split("-", 1)
    h1, m1 = [int(x) for x in a.split(":")]
    h2, m2 = [int(x) for x in b.split(":")]
    return (h1, m1), (h2, m2)

AM_WINDOW_STR = os.environ.get("ABSORB_WINDOW_AM", "08:00-12:00")
PM_WINDOW_STR = os.environ.get("ABSORB_WINDOW_PM", "14:00-18:00")
WINDOWS = {
    "am": _parse_window(AM_WINDOW_STR),
    "pm": _parse_window(PM_WINDOW_STR),
}

GRACE_MIN = int(os.environ.get("ABSORB_GUARD_GRACE_MIN", "5"))

def window_bounds_pt(dt_pt: datetime, which: str):
    """Return (start_dt, end_dt) for the given window 'am'/'pm' on the same calendar day as dt_pt."""
    (h1, m1), (h2, m2) = WINDOWS[which]
    start = dt_pt.replace(hour=h1, minute=m1, second=0, microsecond=0)
    end   = dt_pt.replace(hour=h2, minute=m2, second=0, microsecond=0)
    return start, end

def in_window(dt_pt: datetime, which: str) -> bool:
    start, end = window_bounds_pt(dt_pt, which)
    return start <= dt_pt <= end

def read_log():
    if not LOG_FILE.exists():
        return []
    rows = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                # skip malformed lines
                pass
    return rows

def had_success_for_day(rows, day_str: str, which: str) -> bool:
    # Look for any success (scheduled or catchup) for this day+window
    for r in reversed(rows):
        ts = r.get("ts_utc")
        if not ts:
            continue
        if r.get("event") == "absorb" and r.get("status") == "ok" and r.get("target_window") == which:
            if ts[:10] == day_str:  # YYYY-MM-DD from UTC timestamp
                return True
    return False

def run_catchup(which: str) -> int:
    env = os.environ.copy()
    env["RUN_MODE"] = "catchup"
    env["TARGET_WINDOW"] = which
    cmd = [sys.executable, "tools/absorb_runner.py"]
    print(f"[guard] Triggering catch-up for {which.upper()} window via: {cmd}")
    return subprocess.call(cmd, env=env)

def main():
    rows = read_log()
    now = now_pt()
    today = now.date().isoformat()

    for which in ("am", "pm"):
        start, end = window_bounds_pt(now, which)
        grace_deadline = end + timedelta(minutes=GRACE_MIN)

        if had_success_for_day(rows, today, which):
            print(f"[guard] {today} {which.upper()}: already OK — nothing to do.")
            continue

        if in_window(now, which):
            print(f"[guard] {today} {which.upper()}: inside window ({start.time()}–{end.time()} PT) — waiting.")
            continue

        if now <= grace_deadline:
            print(f"[guard] {today} {which.upper()}: window ended at {end.time()} PT; "
                  f"within grace ({GRACE_MIN} min) — not catching up yet.")
            continue

        # Window has passed + beyond grace + no success logged -> catch up
        rc = run_catchup(which)
        if rc == 0:
            print(f"[guard] {today} {which.upper()}: catch-up SUCCESS (rc=0).")
        else:
            print(f"[guard] {today} {which.upper()}: catch-up FAILED (rc={rc}).")
            # Optional: write an alert line or trigger a local alert file
            # with open('memory/logs/absorb/alerts.log','a',encoding='utf-8') as a:
            #     a.write(f"{datetime.no
