#!/usr/bin/env python3
from datetime import datetime
import pathlib

LOG = pathlib.Path.home() / "consensus-project" / "memory" / "logs" / "system" / "voice_health.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

ts = datetime.utcnow().isoformat() + "Z"
msg = f"{ts} | daily_voice_reminder | OK (stub) — no SMS sent\n"
LOG.write_text((LOG.read_text() if LOG.exists() else "") + msg)
print("daily_voice_reminder: logged OK")
