#!/usr/bin/env python3
import subprocess
import time
import json
import logging
from datetime import datetime
from pathlib import Path

# === Setup logging ===
log_dir = Path("memory/logs/system")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "absorb_guard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("absorb_guard")

STATUS_FILE = log_dir / "last_absorb_status.json"
ABSORB_CMD = ["bash", "tools/absorb_once.sh"]  # adjust if needed


def write_status(status: str, details: str = ""):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"timestamp": ts, "status": status, "details": details}
    with STATUS_FILE.open("w") as f:
        json.dump(payload, f, indent=2)
    logger.info(f"[checkpoint] {payload}")


def run_once():
    for attempt in range(1, 4):  # up to 3 retries
        logger.info(f"[guard] Attempt {attempt}/3")
        try:
            result = subprocess.run(
                ABSORB_CMD, capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                logger.info("[guard] SUCCESS")
                write_status("success")
                return True
            else:
                logger.warning(f"[guard] FAIL rc={result.returncode}")
                logger.warning(result.stderr.strip())
                write_status("failure", f"rc={result.returncode}")
        except Exception as e:
            logger.error(f"[guard] Exception: {e}")
            write_status("error", str(e))
        time.sleep(5)
    return False


def main():
    while True:
        logger.info(f"[guard] Starting absorb_guard at {datetime.utcnow().isoformat()}Z")
        run_once()
        logger.info("[guard] Sleeping 30m before next run...")
        time.sleep(1800)


if __name__ == "__main__":
    main()
