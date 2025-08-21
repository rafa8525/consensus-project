cat > tools/absorb_hourly.py <<'PY'
#!/usr/bin/env python3
import os, sys, json, subprocess
from pathlib import Path
from datetime import datetime, time
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
LOG = Path("memory/logs/absorb/absorb_success_log.jsonl")

AM_START = time(9, 30)   # 09:30
AM_END   = time(10, 29)  # 10:29
PM_START = time(15, 30)  # 15:30
PM_END   = time(16, 29)  # 16:29

def load_log():
    entries = []
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries

def day_has(entries, day_date, window):
    for e in entries:
        if e.get("window") != window:
            continue
        ts = e.get("ts")
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        dt_local = dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)
        if dt_local.date() == day_date:
            return True
    return False

def between(now_t, start_t, end_t):
    return (now_t >= start_t) and (now_t <= end_t)

def run_absorb(window, mode):
    env = os.environ.copy()
    env["RUN_MODE"] = mode
    env["TARGET_WINDOW"] = window
    rc = subprocess.run(["/usr/bin/python3", "tools/absorb_runner.py"], env=env).returncode
    if rc != 0:
        print(f"[absorb_hourly] {window} {mode} run failed (rc={rc})")
        return False
    rc2 = subprocess.run(["/usr/bin/python3", "tools/absorb_log_append.py", window]).returncode
    if rc2 != 0:
        print(f"[absorb_hourly] WARNING: runner ok but logging failed (rc={rc2})")
    else:
        print(f"[absorb_hourly] logged {window} success")
    return True

def main():
    now = datetime.now(TZ)
    today = now.date()
    entries = load_log()
    am_done = day_has(entries, today, "am")
    pm_done = day_has(entries, today, "pm")
    now_t = now.time()

    if not am_done and between(now_t, AM_START, AM_END):
        ok = run_absorb("am", "scheduled"); sys.exit(0 if ok else 1)
    if not pm_done and between(now_t, PM_START, PM_END):
        ok = run_absorb("pm", "scheduled"); sys.exit(0 if ok else 1)

    # Same-day catchups after windows have passed
    if not pm_done and now_t > PM_END:
        ok = run_absorb("pm", "catchup"); sys.exit(0 if ok else 1)
    if not am_done and now_t > AM_END:
        ok = run_absorb("am", "catchup"); sys.exit(0 if ok else 1)

    print("[absorb_hourly] nothing due right now"); sys.exit(0)

if __name__ == "__main__":
    main()
PY
chmod +x tools/absorb_hourly.py
