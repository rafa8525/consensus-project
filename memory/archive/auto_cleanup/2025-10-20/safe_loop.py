#!/usr/bin/env python3
[ -f $LOCK ] && echo safe_loop already running && exit 0
LOCK=$HOME/consensus-project/memory/logs/system/safe_loop.lock
import os, json, time, hashlib
from pathlib import Path
from datetime import datetime

BASE = Path(os.environ.get("PROJECT_DIR") or (Path.home()/ "consensus-project"))
HB  = BASE/"memory/logs/heartbeat/last_heartbeat.txt"
LED = BASE/"memory/logs/system/sms_ledger.jsonl"
Q   = BASE/"memory/queue"
PROC= Q/"processing"; DONE= Q/"done"
for d in [HB.parent, LED.parent, Q, PROC, DONE]: d.mkdir(parents=True, exist_ok=True)

def now(): return datetime.now().isoformat(timespec="seconds")

def write_heartbeat():
    HB.write_text(now()+"\n", encoding="utf-8")

def record_sms(status, to, body, meta=None):
    rec = {"timestamp": now(),"id": hashlib.sha256(f"{to}|{body}|{now()}".encode()).hexdigest()[:12],
           "to": to, "status": status, "body": (body or "")[:200], "meta": meta or {}}
    with LED.open("a", encoding="utf-8") as f: f.write(json.dumps(rec)+"\n")

def process_queue_once():
    for jf in sorted(Q.glob("*.json")):
        tgt = PROC/jf.name
        try: jf.rename(tgt)
        except FileNotFoundError: continue
        try:
            job = json.loads(tgt.read_text(encoding="utf-8"))
        except Exception:
            job = {}
        # never send; just skip/log for visibility
        if job.get("type") == "sms":
            record_sms("SKIP_DISABLED", job.get("to",""), job.get("body",""), {"reason":"safe_loop"})
        (DONE/jf.name).write_text(json.dumps(job), encoding="utf-8")
        tgt.unlink(missing_ok=True)

def main():
    print("[safe_loop] started; SMS is disabled; heartbeat every 10s")
    while True:
        try:
            write_heartbeat()
            process_queue_once()
        except Exception as e:
            # swallow all errors; guard will restart if truly stuck
            pass
        time.sleep(10)

if __name__ == "__main__": main()
