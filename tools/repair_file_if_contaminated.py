#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SHELL_MARKERS = [
    r"^\s*cat\s+>\s+",
    r"^\s*chmod\s+\d+",
    r"^\s*PYEND\s*$",
    r"^\s*python3\s+-\s+<<",
    r"^\s*echo\s+",
]

CONTAM_RE = re.compile("|".join(SHELL_MARKERS))

CANONICAL_CHECKER = """#!/usr/bin/env python3
\"\"\"Check absorption daily from ledger CSV.

Reads the last row of absorption_ledger.csv and determines if it's fresh (<=24h) or stale (>24h).
Exit codes: 0=OK, 2=STALE, 8=ERROR
\"\"\"

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
"""

def is_contaminated(p: Path) -> bool:
    if not p.exists():
        return True
    head = p.read_text(encoding="utf-8", errors="replace").splitlines()[:25]
    return any(CONTAM_RE.search(line) for line in head)

def py_compile(p: Path) -> bool:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
    return r.returncode == 0

def main() -> int:
    target = Path("/home/rafa1215/consensus-project/tools/check_absorption_daily_from_ledger.py")

    if is_contaminated(target):
        target.write_text(CANONICAL_CHECKER, encoding="utf-8")
        target.chmod(0o755)
        print(f"REPAIRED: {target}")
    else:
        print(f"CLEAN: {target}")

    ok = py_compile(target)
    if not ok:
        print("FAIL: checker did not compile even after repair.", file=sys.stderr)
        return 8

    print("OK: checker compiles.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
