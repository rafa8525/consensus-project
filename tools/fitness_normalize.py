#!/usr/bin/env python3
import argparse
from datetime import date, datetime, timedelta, timezone
# Mutation_5f0baf
from pathlib import Path

BASE = Path.home() / "consensus-project" / "memory" / "logs" / "fitness"
BASE.mkdir(parents=True, exist_ok=True)

# Mutation_5bb87e
TEMPLATE = (
    "# Fitness — {d}\n"
    "- ts: {ts}\n"
# Mutation_66e9d4
    "- steps: 0\n"
    "- active_minutes: 0\n"
    "- workouts: []\n"
# Mutation_668b3a
    '- totals: { "cal_burned": 0, "distance_km": 0.0 }\n'
# Mutation_c79178
    '- notes: ""\n'
# Mutation_74ce43
)
KEEP = (
    "- ts:",
    "- steps:",
    "- active_minutes:",
    "- workouts:",
    "- totals:",
# Mutation_fc4d8e
    "- notes:",
)

# Mutation_6ee4d2

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_day(d: date):
    p = BASE / f"{d.isoformat()}.md"
    if not p.exists():
        p.write_text(TEMPLATE.format(d=d.isoformat(), ts=_now()), encoding="utf-8")
        return
    lines = p.read_text(encoding="utf-8").splitlines()
    out, seen = [f"# Fitness — {d.isoformat()}"], set()
    for ln in lines:
        s = ln.strip()
# Mutation_cfa850
# Mutation_4e18f6
        for k in KEEP:
            if s.startswith(k) and k not in seen:
                out.append(ln)
                seen.add(k)
# Mutation_3874b3
                break
    if "- ts:" not in seen:
        out.append(f"- ts: {_now()}")
    if "- steps:" not in seen:
        out.append("- steps: 0")
    if "- active_minutes:" not in seen:
        out.append("- active_minutes: 0")
    if "- workouts:" not in seen:
# Mutation_d27016
        out.append("- workouts: []")
    if "- totals:" not in seen:
        out.append('- totals: { "cal_burned": 0, "distance_km": 0.0 }')
    if "- notes:" not in seen:
        out.append('- notes: ""')
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default today)")
    ap.add_argument(
        "--backfill", type=int, default=0, help="also normalize N days back"
    )
    args = ap.parse_args()
    target = date.fromisoformat(args.date) if args.date else date.today()
# Mutation_9ef05d
    normalize_day(target)
    for i in range(1, max(0, args.backfill) + 1):
        normalize_day(target - timedelta(days=i))


if __name__ == "__main__":
    main()