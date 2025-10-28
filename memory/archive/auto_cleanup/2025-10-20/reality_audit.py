#!/usr/bin/env python3
from pathlib import Path
import json, datetime

ROOT = Path.home() / "consensus-project"
SYSLOG = ROOT / "memory" / "logs" / "system"
AUDIT_DIR = SYSLOG / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def latest_file(pattern):
    files = sorted(SYSLOG.glob(pattern),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

int_file = latest_file("integration_manifest_*.json")
mem_file = latest_file("manifest_*.json")

report = {"checked_on": str(datetime.datetime.now()),
          "integration": str(int_file),
          "memory": str(mem_file),
          "differences": {}}

if not int_file or not mem_file:
    report["error"] = "Missing manifest(s). Run integration_manifest.py and log_memory_manifest.py first."
else:
    integration = json.loads(int_file.read_text())
    memory = json.loads(mem_file.read_text())
    for mod, info in integration.items():
        sha = info.get("sha256")
        if sha and sha not in memory.values():
            report["differences"][mod] = "hash_not_found_in_memory"
        elif info["status"] == "missing":
            report["differences"][mod] = "declared_but_missing"
        else:
            report["differences"][mod] = "verified"

out = AUDIT_DIR / f"reality_audit_{datetime.date.today()}.json"
out.write_text(json.dumps(report, indent=2))
print(f"🔎 Reality audit complete: {out}")
