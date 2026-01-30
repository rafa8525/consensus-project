#!/usr/bin/env python3
"""Check absorption daily from ledger CSV.

Reads the last row of absorption_ledger.csv and determines if it's fresh (<=24h) or stale (>24h).
Exit codes: 0=OK, 2=STALE, 8=ERROR
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER_PATH = Path("/home/rafa1215/memory/logs/status/absorption_ledger.csv")
MAX_HOURS = 24.0


def main() -> int:
    if not LEDGER_PATH.exists():
        print("Absorption daily check (ledger): ERROR")
        print("Last success (UTC): N/A")
        print("Age hours: N/A")
        print("Error: Ledger file not found", file=sys.stderr)
        return 8

    try:
        with LEDGER_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            last_row = None
            for row in reader:
                last_row = row

        if not last_row:
            print("Absorption daily check (ledger): ERROR")
            print("Last success (UTC): N/A")
            print("Age hours: N/A")
            print("Error: Ledger has no data rows", file=sys.stderr)
            return 8

        ts = (last_row.get("timestamp_utc") or "").strip()
        if not ts:
            print("Absorption daily check (ledger): ERROR")
            print("Last success (UTC): N/A")
            print("Age hours: N/A")
            print("Error: Missing timestamp_utc column/value", file=sys.stderr)
            return 8

        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"

        last_ts = datetime.fromisoformat(ts)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        else:
            last_ts = last_ts.astimezone(timezone.utc)

        now = datetime.now(timezone.utc)
        age_hours = (now - last_ts).total_seconds() / 3600.0

        if age_hours <= MAX_HOURS:
            status, exit_code = "OK", 0
        else:
            status, exit_code = "STALE", 2

        print(f"Absorption daily check (ledger): {status}")
        print(f"Last success (UTC): {last_ts.isoformat()}")
        print(f"Age hours: {age_hours:.2f}")
        return exit_code

    except Exception as e:
        print("Absorption daily check (ledger): ERROR")
        print("Last success (UTC): N/A")
        print("Age hours: N/A")
        print(f"Error: {e}", file=sys.stderr)
        return 8


if __name__ == "__main__":
    raise SystemExit(main())
