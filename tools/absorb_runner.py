#!/usr/bin/env python3
# absorb_runner.py — runs real absorber (absorb_memory.py)

import subprocess
import sys
from datetime import datetime

LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/system/absorb_runner.log"
ABSORB_SCRIPT = "/home/rafa1215/consensus-project/tools/absorb_memory.py"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as logf:
        logf.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def run_absorb():
    try:
        log(f"🔁 Starting {ABSORB_SCRIPT}...")

        result = subprocess.run(
            ["/usr/bin/python3", ABSORB_SCRIPT],
            check=True,
            capture_output=True,
            text=True
        )

        log("✅ absorb_memory.py completed successfully.")
        if result.stdout:
            log(result.stdout)

    except subprocess.CalledProcessError as e:
        log("❌ absorb_memory.py FAILED.")
        if e.stderr:
            log(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_absorb()
