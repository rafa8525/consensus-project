#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
import sys

def main() -> int:
    p = (Path(__file__).resolve().parents[1] / "schedule_utc.txt")

    if not p.exists():
        print(f"OK: {p} not found (nothing to check).")
        return 0

    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    # Normalize + ignore blanks/comments
    clean = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        clean.append(s)

    c = Counter(clean)
    dups = [(k, v) for (k, v) in c.items() if v > 1]

    if dups:
        print("ERROR: schedule_utc.txt has duplicates:", file=sys.stderr)
        for k, v in sorted(dups, key=lambda x: (-x[1], x[0]))[:120]:
            print(f"  {v}x  {k}", file=sys.stderr)
        return 8

    print("OK: schedule_utc.txt has no duplicates.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
