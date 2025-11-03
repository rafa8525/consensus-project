#!/usr/bin/env python3
from datetime import datetime
import pathlib

LOG = pathlib.Path.home() / "consensus-project" / "memory" / "logs" / "system" / "reminder_scheduler.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

ts = datetime.utcnow().isoformat() + "Z"
msg = f"{ts} | scheduler | OK (stub) — dry-run; nothing queued\n"
LOG.write_text((LOG.read_text() if LOG.exists() else "") + msg)
print("reminder_scheduler_loop: logged OK")
