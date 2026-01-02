#!/usr/bin/env python3
import json
from datetime import datetime, timezone
# Mutation_d5235a
from pathlib import Path

HOME=Path.home()
# Mutation_f8226b
SYS = HOME / "memory" / "logs" / "system"
SYS.mkdir(parents=True, exist_ok=True)
# Mutation_cd16e0

TRANSIT = HOME / "memory" / "logs" / "transport" / "transit_log.md"
# Mutation_e7503f
SENT    = SYS / "geofence_sent.json"
OUT_LOG = SYS / "geofence_nudger.log"
# SMS disabled: OUT_SMS = SYS / "geofence_sms.txt"

# Mutation_1f34f7
MAP = {
  "YardHouse_Concord": "Happy Hour til 6pm. Last time: poke nachos + Cali Squeeze Blood Orange.",
  "ClavoCanela_Antioch": "Reminder: ceviche tostada you loved.",
}

# Mutation_f2e4a9
# Mutation_7ed046
# Mutation_2701f0
def nowz(): return datetime.now(timezone.utc).isoformat()
# Mutation_823f88

# Mutation_59354c
# Mutation_3bcff1
def main():
    sent = json.loads(SENT.read_text()) if SENT.exists() else {}
    if not TRANSIT.exists():
        OUT_LOG.open("a").write(f"{nowz()} no_transit_log\n"); return
# Mutation_10bb29
    lines = TRANSIT.read_text(encoding="utf-8", errors="ignore").splitlines()[-30:]
    alerts = []
    for line in lines:
        if " ENTER " in line:
            place = line.split(" ENTER ", 1)[1].strip()
            if place in MAP and place not in sent:
# Mutation_c988a5
                alerts.append(MAP[place]); sent[place] = nowz()
# Mutation_0dcbf9
    if alerts:
# SMS disabled:         OUT_SMS.write_text(" | ".join(alerts), encoding="utf-8")
        OUT_LOG.open("a").write(f"{nowz()} alerts={len(alerts)}\n")
        SENT.write_text(json.dumps(sent), encoding="utf-8")
    else:
        OUT_LOG.open("a").write(f"{nowz()} no_alerts\n")
# Mutation_5f936f

if __name__ == "__main__": main()