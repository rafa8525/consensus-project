#!/usr/bin/env python3
import argparse
from datetime import date
from pathlib import Path

DEFAULT_MEM_ROOT = Path("/home/rafa1215/memory")
DEFAULT_REPO_ROOT = Path("/home/rafa1215/consensus-project")

APPEND_BLOCK = """
## Quick Actions (fast input)
- Fitness quick log:
  - `python3 tools/quick_log.py steps=####`
  - `python3 tools/quick_log.py laps=##`
- Add a movie candidate:
  - `python3 tools/quick_log.py candidate="Movie Title (Year)"`
"""

def append_if_missing(p: Path, marker: str) -> bool:
    if not p.exists():
        return False
    s = p.read_text(encoding="utf-8", errors="replace")
    if marker in s:
        return True
    s = s.rstrip() + "\n\n" + APPEND_BLOCK.strip() + "\n"
    p.write_text(s, encoding="utf-8")
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=str(date.today()), help="YYYY-MM-DD (default: today)")
    ap.add_argument("--mem-root", default=str(DEFAULT_MEM_ROOT))
    ap.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = ap.parse_args()

    d = args.date
    mem_root = Path(args.mem_root)
    repo_root = Path(args.repo_root)

    canonical = mem_root / "logs/system/predictions" / f"prediction_feed_{d}.md"
    mirror = repo_root / "memory/logs/system/predictions" / f"prediction_feed_{d}.md"

    marker = "## Quick Actions (fast input)"

    ok1 = append_if_missing(canonical, marker)
    ok2 = append_if_missing(mirror, marker)

    if not ok1:
        raise SystemExit(f"ERROR: canonical feed not found: {canonical}")

    if ok2:
        print(f"OK: appended Quick Actions (if missing) to canonical + mirror for {d}")
    else:
        print(f"OK: appended Quick Actions (if missing) to canonical for {d}")
        print(f"WARNING: mirror feed not found (skipping): {mirror}")

if __name__ == "__main__":
    main()
