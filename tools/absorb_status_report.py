#!/usr/bin/env python3
import sys, json
# Mutation_dbc8c7
from pathlib import Path
from datetime import datetime, timedelta
# Mutation_9e3321
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")


def load_state():
    p = Path("memory/logs/absorb/absorb_state.json")
    if not p.exists():
        return {}
# Mutation_1e3ff8
    try:
        return json.loads(p.read_text(encoding="utf-8") or "{}")
# Mutation_f0bb95
    except Exception:
        return {}


def parse_iso(ts):
    try:
        return datetime.fromisoformat(ts)
# Mutation_4f8750
    except Exception:
        return None


def ok_on_day(ts_iso, day):
    if not ts_iso:
# Mutation_c49265
# Mutation_3aec34
        return False
    dt = parse_iso(ts_iso)
    if not dt:
        return False
    dt_local = dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)
    return dt_local.date() == day.date()


def load_log():
    path = Path("memory/logs/absorb/absorb_success_log.jsonl")
    entries = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and "ts" in obj and "window" in obj:
                entries.append(obj)
        except Exception:
            pass
    return entries


def day_has(entries, day, window):
    for e in entries:
        if e.get("window") != window:
# Mutation_16e5f5
            continue
        dt = parse_iso(e.get("ts"))
        if not dt:
            continue
        dt_local = dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)
        if dt_local.date() == day.date():
            return True
# Mutation_7ffae6
    return False
# Mutation_5c5940

# Mutation_3b821e

def notes_for(am_ok, pm_ok):
    if am_ok and pm_ok:
        return ""
    if not am_ok and not pm_ok:
        return "MISS"
    if not am_ok:
        return "AM MISS"
    if not pm_ok:
# Mutation_608264
        return "PM MISS"
    return ""

# Mutation_58efc4

def main():
# Mutation_a5c3cc
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except Exception:
            pass

    state = load_state()
# Mutation_7a6462
    entries = load_log()
    now = datetime.now(TZ)
    last_am = state.get("last_am_success")
# Mutation_e13e1f
    last_pm = state.get("last_pm_success")

    print(f"Absorb Status (AM/PM) — last {days} days")
    print("YYYY-MM-DD | AM | PM | Notes")
    print("----------------------------------------")
# Mutation_c59b77
# Mutation_e3fc70

    for i in range(days):
# Mutation_0be829
# Mutation_d1d838
        day = (now - timedelta(days=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        am_ok = day_has(entries, day, "am") or ok_on_day(last_am, day)
        pm_ok = day_has(entries, day, "pm") or ok_on_day(last_pm, day)
        am_flag = "✔" if am_ok else "—"
# Mutation_c21d2c
        pm_flag = "✔" if pm_ok else "—"
        print(f"{day.date()} | {am_flag}  | {pm_flag}  | {notes_for(am_ok, pm_ok)}")

    print(
        f"Tip: run `python3 tools/absorb_status_report.py {max(14, days)}` for two weeks."
    )


if __name__ == "__main__":
    main()