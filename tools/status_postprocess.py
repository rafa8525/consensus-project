#!/usr/bin/env python3
"""
Append Ride Deals (summary) to today's Project Status (logs-only).
- Reads:  ~/memory/logs/system/ride_deals.json
- Appends to: ~/memory/logs/reports/project_status_YYYY-MM-DD.md
"""

import json, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
LOGS = HOME / "memory" / "logs"
REPORTS = LOGS / "reports"
STATUS = REPORTS / f"project_status_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
RIDE = LOGS / "system" / "ride_deals.json"

def main():
    if not STATUS.exists():
        print(f"[status_postprocess] No status file for today: {STATUS}", file=sys.stderr)
        return 0

    lines = []
    lines.append("\n### Ride Deals (summary)\n")
    if RIDE.exists():
        try:
            data = json.loads(RIDE.read_text(encoding="utf-8", errors="ignore") or "{}")
            sites = data.get("sites", [])
            if not sites:
                lines.append("- (no data)\n")
            else:
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
            lines.append(f"- (ride deals parse error: {e})\n")
    else:
        lines.append("- (ride_deals.json missing)\n")

    with STATUS.open("a", encoding="utf-8") as f:
        f.writelines(lines)

    (LOGS/"system"/"status_postprocess.log").open("a", encoding="utf-8").write(
        f"{datetime.now(timezone.utc).isoformat()} appended ride-deals summary to {STATUS.name}\n"
    )
    print("[status_postprocess] appended Ride Deals (summary)")

if __name__ == "__main__":
    raise SystemExit(main())
