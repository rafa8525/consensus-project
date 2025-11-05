#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

HOME=Path.home()
SYS = HOME / "memory" / "logs" / "system"
SYS.mkdir(parents=True, exist_ok=True)

TRANSIT = HOME / "memory" / "logs" / "transport" / "transit_log.md"
SENT    = SYS / "geofence_sent.json"
OUT_LOG = SYS / "geofence_nudger.log"
# SMS disabled: OUT_SMS = SYS / "geofence_sms.txt"

MAP = {
  "YardHouse_Concord": "Happy Hour til 6pm. Last time: poke nachos + Cali Squeeze Blood Orange.",
  "ClavoCanela_Antioch": "Reminder: ceviche tostada you loved.",
}

def nowz(): return datetime.now(timezone.utc).isoformat()

def main():
    sent = json.loads(SENT.read_text()) if SENT.exists() else {}
    if not TRANSIT.exists():
        OUT_LOG.open("a").write(f"{nowz()} no_transit_log\n"); return
    lines = TRANSIT.read_text(encoding="utf-8", errors="ignore").splitlines()[-30:]
    alerts = []
    for line in lines:
        if " ENTER " in line:
            place = line.split(" ENTER ", 1)[1].strip()
            if place in MAP and place not in sent:
                alerts.append(MAP[place]); sent[place] = nowz()
    if alerts:
# SMS disabled:         OUT_SMS.write_text(" | ".join(alerts), encoding="utf-8")
        OUT_LOG.open("a").write(f"{nowz()} alerts={len(alerts)}\n")
        SENT.write_text(json.dumps(sent), encoding="utf-8")
    else:
        OUT_LOG.open("a").write(f"{nowz()} no_alerts\n")

if __name__ == "__main__": main()
