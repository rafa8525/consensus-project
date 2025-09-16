#!/usr/bin/env python3
import json, os, sys, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

LOG_DIR = Path("memory/logs/absorb")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "absorb_log.jsonl"

ABSORB_CMD = os.environ.get("ABSORB_CMD", "").strip()
if not ABSORB_CMD:
    # Fallback: point to your real absorb command/script
    # Example: export ABSORB_CMD="/home/rafa1215/consensus-project/tools/absorb_and_sync.sh"
    print("ERROR: ABSORB_CMD not set", file=sys.stderr)
    sys.exit(2)

def log(event: dict):
    event["ts_utc"] = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def main():
    mode = os.environ.get("RUN_MODE", "scheduled")  # "scheduled" or "catchup"
    target = os.environ.get("TARGET_WINDOW", "am")  # "am" or "pm"

    max_retries = int(os.environ.get("ABSORB_MAX_RETRIES", "3"))
    backoff = [60, 300, 900]  # 1 min, 5 min, 15 min delays

    for attempt in range(1, max_retries + 1):
        started = time.time()
        try:
            r = subprocess.run(
                ABSORB_CMD,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60*30
            )
            ok = (r.returncode == 0)
            log({
                "event": "absorb",
                "mode": mode,
                "target_window": target,
                "attempt": attempt,
                "status": "ok" if ok else "fail",
                "rc": r.returncode,
                "stdout": r.stdout[-4000:],  # last 4000 chars
                "stderr": r.stderr[-4000:],
                "duration_s": round(time.time() - started, 3),
            })
            if ok:
                sys.exit(0)
        except Exception as e:
            log({
                "event": "absorb",
                "mode": mode,
                "target_window": target,
                "attempt": attempt,
                "status": "error",
                "error": repr(e),
                "duration_s": round(time.time() - started, 3),
            })

        # wait before retry if not last attempt
        if attempt < max_retries:
            time.sleep(backoff[min(attempt - 1, len(backoff) - 1)])

    # all retries failed
    sys.exit(1)

if __name__ == "__main__":
    main()
