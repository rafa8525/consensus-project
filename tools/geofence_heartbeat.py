#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
root = Path(__file__).resolve().parent.parent
logd = root / "memory" / "logs" / "geofencing"
logd.mkdir(parents=True, exist_ok=True)
d = datetime.now(timezone.utc).date().isoformat()
p = logd / f"heartbeat_{d}.md"
p.write_text((p.read_text() if p.exists() else "") + f"[{datetime.now(timezone.utc).isoformat()}] heartbeat OK\n", encoding="utf-8")
print("OK")
