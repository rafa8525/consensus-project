#!/usr/bin/env python3
import argparse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = Path.home() / "consensus-project" / "memory" / "logs" / "fitness"
BASE.mkdir(parents=True, exist_ok=True)

TEMPLATE = (
    "# Fitness — {d}\n"
    "- ts: {ts}\n"
    "- steps: 0\n"
    "- active_minutes: 0\n"
    "- workouts: []\n"
    '- totals: { "cal_burned": 0, "distance_km": 0.0 }\n'
    '- notes: ""\n'
)

KEEP_KEYS = ("- ts:", "- steps:", "- active_minutes:", "- workouts:", "- totals:", "- notes:")

def normalize_day(d: date):
    p = BASE / f"{d.isoformat()}.md"
    if not p.exists():
        p.write_text(TEMPLATE.format(d=d.isoformat(), ts=_now()), encoding="utf-8")
        return p

    lines = p.read_text(encoding="utf-8").splitlines()
    out, seen = [], set()

    # header
    out.append(f"# Fitness — {d.isoformat()}")

    # keep only the first occurrence of each key, drop filler/duplicates
    for ln in lines:
        s = ln.strip()
        for k in KEEP_KEYS:
            if s.startswith(k) and k not in seen:
                # strip any ancient filler if ever present (none expected here)
                out.append(ln)
                seen.add(k)
                break

    # fill missing keys
    if "- ts:" not in seen:
        out.append(f"- ts: {_now()}")
    if "- steps:" not in seen:
        out.append("- steps: 0")
    if "- active_minutes:" not in seen:
        out.append("- active_minutes: 0")
    if "- workouts:" not in seen:
        out.append("- workouts: []")
    if "- totals:" not in seen:
        out.append('- totals: { "cal_burned": 0, "distance_km": 0.0 }')
    if "- notes:" not in seen:
        out.append('- notes: ""')

    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return p

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--backfill", type=int, default=0, help="also normalize N days back")
    args = ap.parse_args()

    target = date.fromisoformat(args.date) if args.date else date.today()
    normalize_day(target)
    for i in range(1, max(0, args.backfill) + 1):
        normalize_day(target - timedelta(days=i))

if __name__ == "__main__":
    main()
