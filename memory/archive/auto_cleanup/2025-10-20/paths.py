from pathlib import Path
import os

BASE = Path(os.environ.get("PROJECT_DIR") or (Path.home() / "consensus-project"))
LOG_DIR = BASE / "memory" / "logs" / "system"
HB_FILE = BASE / "memory" / "logs" / "heartbeat" / "last_heartbeat.txt"
QUEUE = BASE / "memory" / "queue"
Q_PROC = QUEUE / "processing"
Q_DONE = QUEUE / "done"
LEDGER = LOG_DIR / "sms_ledger.jsonl"
LOCK = LOG_DIR / "mcl_v2.lock"
MAIN_LOG = LOG_DIR / "mcl_v2.log"
ERR_LOG = LOG_DIR / "mcl_v2_errors.log"

def ensure_dirs() -> None:
    for d in (LOG_DIR, HB_FILE.parent, QUEUE, Q_PROC, Q_DONE, LEDGER.parent):
        d.mkdir(parents=True, exist_ok=True)

ensure_dirs()
