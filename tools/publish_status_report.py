#!/usr/bin/env python3
import datetime
from pathlib import Path

HOME = Path.home()
LOGS = HOME / "memory" / "logs"
OUT  = LOGS / "reports" / f"project_status_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}.md"
OUT.parent.mkdir(parents=True, exist_ok=True)

SECTIONS = [
    ("system/kb_smoke.log",            "KB Smoke"),
    ("system/knowledge_share_kpi.log", "Knowledge Share KPI"),
    ("system/vpn_daily_report.log",    "VPN Daily Report"),
    ("system/fitness_audit.log",       "Fitness Audit"),
    ("system/mcl_guard_heartbeat.log", "Guard Heartbeat (tail)"),
]

lines = [
    "# Project Status",
    f"Date (UTC): {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}",
    "",
    "## Health checks",
]

for rel, title in SECTIONS:
    p = LOGS / rel
    lines.append(f"\n### {title}\n")
    if p.exists():
        tail = p.read_text(encoding="utf-8", errors="ignore").splitlines()[-5:]
        lines.extend(tail if tail else ["(no recent lines)"])
    else:
        lines.append("(missing)")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- Ride Deals pretty printer (append if present) ---
try:
    import json
    from pathlib import Path as _P
    LOGS = _P.home()/"memory"/"logs"
    rj = LOGS/"system"/"ride_deals.json"
    if rj.exists():
        data = json.loads(rj.read_text(encoding="utf-8", errors="ignore") or "{}")
        sites = data.get("sites", [])
        lines.append("\n### Ride Deals (summary)\n")
        for it in sites:
            site = it.get("site","?")
            count = len(it.get("hits", [])) if "hits" in it else "ERR"
            lines.append(f"- {site} — {count}")
except Exception:
    pass
