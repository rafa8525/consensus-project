#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
p = Path("memory/logs/scheduler/heartbeat_logger.log"); p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(f"[{datetime.now().isoformat(timespec='seconds')}] (stub) heartbeat_logger OK\n", encoding="utf-8")
print("heartbeat_logger stub OK")
