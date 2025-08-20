#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
LOG_FILE = Path("memory/logs/absorb/absorb_log.jsonl")

# Define your “intended” windows (Pacific time)
# AM window: 10:00 PT target, valid 08:00–12:00
# PM window: 16:00 PT target, valid 14:00–18:00
PT_OFFSET = -7  # PDT; switch to -8 for PST or compute via zoneinfo if available
def now_pt():
    return datetime.utcnow() + timedelta(hours=PT_OFFSET)

WINDOWS = {
    "am": {"start": (8, 0), "end": (12, 0)},
    "pm": {"start": (14, 0), "end": (18, 0)},
}

def in_window(dt_pt, which):
    h1,m1 = WINDOWS[which]["start"]
    h2,m2 = WINDOWS[which]["end"]
    start = dt_pt.replace(hour=h1, minute=m1, second=0, microsecond=0)
    end   = dt_pt.replace(hour=h2, minute=m2, second=0, microsecond=0)
    return start <= dt_pt <= end

def read_log():
    if not LOG_FILE.exists():
        return []
    rows = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                pass
    return rows

def had_success_for_day(rows, day_str, which):
    for r in reversed(rows):
        ts = r.get("ts_utc")
        if not ts: 
            continue
        if r.get("event")=="absorb" and r.get("status")=="ok":
            d = ts[:10]  # YYYY-MM-DD
            if d==day_str and r.get("target_window")==which:
                return True
    return False

def run_catchup(which):
    env = os.environ.copy()
    env["RUN_MODE"] = "catchup"
    env["TARGET_WINDOW"] = which
    cmd = [sys.executable, "tools/absorb_runner.py"]
    return subprocess.call(cmd, env=env)

def main():
    rows = read_log()
    now = now_pt()
    today = now.date().isoformat()

    # For each window, decide: OK, still pending, or missed+catchup
    for which in ("am","pm"):
        # If already successful today, skip
        if had_success_for_day(rows, today, which):
            continue
        # If we’re still inside the window, do nothing (scheduled job should hit)
        if in_window(now, which):
            continue
        # If window has passed and success not logged -> run catch-up
        # (also covers the case where scheduled job failed silently)
        rc = run_catchup(which)
        # Optional: if rc!=0, you could trigger your SMS/voice escalation here

if __name__ == "__main__":
    main()
