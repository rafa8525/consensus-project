#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

LOG_FILE = Path("memory/logs/absorb/absorb_log.jsonl")

def read_rows():
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

def has_ok(rows, ymd, which):
    for r in rows:
        if r.get("event")=="absorb" and r.get("status")=="ok" and r.get("target_window")==which:
            if r.get("ts_utc","")[:10]==ymd:
                return True
    return False

def main(days=7):
    rows = read_rows()
    today = datetime.now(timezone.utc).date()
    print("Absorb Status (AM/PM) — last", days, "days")
    print("YYYY-MM-DD | AM | PM | Notes")
    print("-"*40)
    for i in range(days):
        d = today - timedelta(days=i)
        ymd = d.isoformat()
        am_ok = "✔" if has_ok(rows, ymd, "am") else "—"
        pm_ok = "✔" if has_ok(rows, ymd, "pm") else "—"
        note = ""
        if am_ok=="—" or pm_ok=="—":
            note = "MISS"
        print(f"{ymd} | {am_ok}  | {pm_ok}  | {note}")
    print("\nTip: run `python3 tools/absorb_status_report.py 14` for two weeks.")

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv)>1 else 7
    main(days)
