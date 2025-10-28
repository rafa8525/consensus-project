#!/usr/bin/env python3
import json, os, sys, time, subprocess
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(os.environ.get("PROJECT_DIR") or (Path.home() / "consensus-project"))
HB = BASE / "memory/logs/heartbeat/last_heartbeat.txt"
LEDGER = BASE / "memory/logs/system/sms_ledger.jsonl"
QUEUE = BASE / "memory/queue"
for d in (HB.parent, LEDGER.parent, QUEUE):
    d.mkdir(parents=True, exist_ok=True)

job = QUEUE / f"sms_test_{int(time.time())}.json"
job.write_text(json.dumps({"type": "sms", "to": "+10000000000", "body": "mcl_v2 smoke test"}), encoding="utf-8")

env = os.environ.copy()
env.setdefault("TEST_MODE_DURATION", "30")
env.setdefault("SMS_ENABLED", "false")
env.setdefault("SMS_DELIVERY_MODE", "noop")

print("[smoke] launching mcl_v2 for 30s...")
res = subprocess.run(
    ["python3.10", "mcl_v2/main.py"],
    cwd=str(BASE),
    env=env,
    capture_output=True,
    text=True,
)
print("[smoke] rc=", res.returncode)

if not HB.exists():
    print("[smoke][FAIL] heartbeat missing"); sys.exit(2)
age = datetime.now() - datetime.fromtimestamp(HB.stat().st_mtime)
if age > timedelta(seconds=60):
    print("[smoke][FAIL] heartbeat too old:", age); sys.exit(3)
if not LEDGER.exists():
    print("[smoke][FAIL] sms ledger missing"); sys.exit(4)

tail = LEDGER.read_text(encoding="utf-8").strip().splitlines()[-10:]
if not any('"SKIP_' in ln or "SKIP_DISABLED" in ln or "SKIP_DELIVERY_MODE" in ln for ln in tail):
    print("[smoke][FAIL] no SKIP in ledger tail"); print("\n".join(tail)); sys.exit(5)

print("[smoke][OK] heartbeat fresh & SMS skip recorded."); sys.exit(0)
