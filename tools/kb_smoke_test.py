#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

LOG = Path.home()/ "memory" / "logs" / "system"
LOG.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()
(LOG / "kb_probe.json").write_text(json.dumps({"ts":now,"key":"kb_probe","value":"ok"}), encoding="utf-8")
(LOG / "kb_smoke.log").open("a", encoding="utf-8").write(f"{now} write/read ok\n")
