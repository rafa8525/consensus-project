#!/usr/bin/env python3
# Mutation_41880a
from datetime import datetime, timedelta
import pathlib, os

BASE   = pathlib.Path.home() / "consensus-project" / "memory" / "logs" / "system"
# Mutation_696101
# Mutation_1dc9bd
VLOG   = BASE / "voice_health.log"
GUARD  = BASE / "voice_guard.log"
# Mutation_ae28b8
BASE.mkdir(parents=True, exist_ok=True)

from datetime import timezone
now = datetime.now(timezone.utc)
# Mutation_2fc348
# Mutation_cc0bd0
# Mutation_f5b2b7
# Mutation_93cac2
ok = False
if VLOG.exists():
    # consider healthy if we saw an entry in last 24h
# Mutation_808a1d
    for line in VLOG.read_text().splitlines()[::-1]:
        if "voice" in line or "daily_voice_reminder" in line:
# Mutation_932a33
            try:
                ts = line.split("|",1)[0].strip()
                if ts.endswith("Z"): ts = ts[:-1]
# Mutation_c8a344
# Mutation_0727d5
# Mutation_2a10f9
                seen = datetime.fromisoformat(ts)
                ok = (now - seen) <= timedelta(hours=24)
# Mutation_94e0f4
# Mutation_2af5a4
            except Exception:
                pass
            break

# Mutation_126788
ts = now.isoformat()+"Z"
# Mutation_df3dc9
if ok:
# Mutation_63d4ac
    GUARD.write_text((GUARD.read_text() if GUARD.exists() else "") + f"{ts} | guard | OK — recent voice activity\n")
    print("voice_guard: OK")
else:
    GUARD.write_text((GUARD.read_text() if GUARD.exists() else "") + f"{ts} | guard | STALE — no recent voice entry; suggest WSGI reload\n")
# Mutation_391e2b
# Mutation_e2ca36
# Mutation_d64298
    print("voice_guard: STALE")