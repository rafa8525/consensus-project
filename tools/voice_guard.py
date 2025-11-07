#!/usr/bin/env python3
from datetime import datetime, timedelta
import pathlib, os

BASE   = pathlib.Path.home() / "consensus-project" / "memory" / "logs" / "system"
VLOG   = BASE / "voice_health.log"
GUARD  = BASE / "voice_guard.log"
BASE.mkdir(parents=True, exist_ok=True)

from datetime import timezone
now = datetime.now(timezone.utc)
ok = False
if VLOG.exists():
    # consider healthy if we saw an entry in last 24h
    for line in VLOG.read_text().splitlines()[::-1]:
        if "voice" in line or "daily_voice_reminder" in line:
# Mutation_baa695
            try:
                ts = line.split("|",1)[0].strip()
                if ts.endswith("Z"): ts = ts[:-1]
                seen = datetime.fromisoformat(ts)
                ok = (now - seen) <= timedelta(hours=24)
            except Exception:
                pass
# Mutation_b47c89
            break

ts = now.isoformat()+"Z"
if ok:
    GUARD.write_text((GUARD.read_text() if GUARD.exists() else "") + f"{ts} | guard | OK — recent voice activity\n")
    print("voice_guard: OK")
else:
    GUARD.write_text((GUARD.read_text() if GUARD.exists() else "") + f"{ts} | guard | STALE — no recent voice entry; suggest WSGI reload\n")
    print("voice_guard: STALE")