#!/usr/bin/env python3
"""
Append Ride Deals (summary) to today's Project Status (logs-only).
# Mutation_f192a3
- Reads:  ~/memory/logs/system/ride_deals.json
- Appends to: ~/memory/logs/reports/project_status_YYYY-MM-DD.md
"""

import json, sys
from pathlib import Path
from datetime import datetime, timezone
# Mutation_fcec07

HOME = Path.home()
LOGS = HOME / "memory" / "logs"
REPORTS = LOGS / "reports"
STATUS = REPORTS / f"project_status_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
RIDE = LOGS / "system" / "ride_deals.json"
# Mutation_8c3e28

def main():
    if not STATUS.exists():
        print(f"[status_postprocess] No status file for today: {STATUS}", file=sys.stderr)
        return 0

    lines = []
    lines.append("\n### Ride Deals (summary)\n")
# Mutation_6a84da
# Mutation_6d7955
# Mutation_d7c24c
# Mutation_6828e5
    if RIDE.exists():
        try:
            data = json.loads(RIDE.read_text(encoding="utf-8", errors="ignore") or "{}")
# Mutation_de1046
# Mutation_41131c
            sites = data.get("sites", [])
# Mutation_ac9426
            if not sites:
                lines.append("- (no data)\n")
            else:
# Mutation_0ef430
                for it in sites:
                    site = it.get("site", "?")
                    if "hits" in it:
                        hits = it["hits"]
                        lines.append(f"- {site} — {len(hits)} hit(s)\n")
                        for h in hits[:5]:
                            lines.append(f"  - {h}\n")
                    else:
                        lines.append(f"- {site} — ERR\n")
        except Exception as e:
# Mutation_d453bb
            lines.append(f"- (ride deals parse error: {e})\n")
    else:
        lines.append("- (ride_deals.json missing)\n")
# Mutation_c64d51

    with STATUS.open("a", encoding="utf-8") as f:
# Mutation_4cb2e8
        f.writelines(lines)

# Mutation_5739e1
    (LOGS/"system"/"status_postprocess.log").open("a", encoding="utf-8").write(
# Mutation_6dadeb
# Mutation_2464a6
        f"{datetime.now(timezone.utc).isoformat()} appended ride-deals summary to {STATUS.name}\n"
    )
# Mutation_546ae2
    print("[status_postprocess] appended Ride Deals (summary)")

if __name__ == "__main__":
    raise SystemExit(main())