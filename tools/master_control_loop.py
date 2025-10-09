#!/usr/bin/env python3
"""
Master Control Loop (v2025.10.08)
AI Consensus System — Self-Evolution Edition
------------------------------------------------
Orchestrates daily agent tasks, shared intelligence aggregation,
and recursive self-improvement cycles.
"""

import subprocess
import time
from datetime import datetime
from pathlib import Path
import logging
import sys

# -----------------------
# CONFIGURATION
# -----------------------
BASE_DIR = Path("/home/rafa1215/consensus-project")
TOOLS_DIR = BASE_DIR / "tools"
LOG_FILE = BASE_DIR / "memory/logs/system/master_control_log.md"

# Core modules
SHARED_INTELLIGENCE = TOOLS_DIR / "shared_intelligence_loop.py"
RECURSIVE_EVOLUTION = TOOLS_DIR / "recursive_evolution_loop.py"
HEARTBEAT_SCHEDULER = TOOLS_DIR / "heartbeat_scheduler_loop.py"

# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[{asctime}] {levelname}: {message}",
    style="{"
)

def log_console(message: str):
    print(message)
    logging.info(message)

# -----------------------
# MODULE EXECUTION HELPERS
# -----------------------
def run_module(script_path: Path, description: str):
    """Execute a module and log its result."""
    try:
        log_console(f"▶ Starting: {description}")
        subprocess.run(["python3", str(script_path)], check=True)
        log_console(f"✅ Completed: {description}")
    except subprocess.CalledProcessError as e:
        log_console(f"⚠️ Error while running {description}: {e}")
    except Exception as ex:
        log_console(f"❌ Unexpected failure in {description}: {ex}")

# -----------------------
# CORE CYCLE
# -----------------------
def run_master_cycle():
    log_console("🚀 Master Control Loop started.")
    start_time = datetime.now()

    # 1. Run heartbeat
    run_module(HEARTBEAT_SCHEDULER, "Heartbeat Scheduler")

    # 2. Run shared intelligence sync
    run_module(SHARED_INTELLIGENCE, "Shared Intelligence Loop")

    # 3. Run recursive self-evolution test
    run_module(RECURSIVE_EVOLUTION, "Recursive Evolution Loop")

    # 4. Wrap up
    duration = (datetime.now() - start_time).total_seconds()
    log_console(f"🏁 Cycle completed in {duration:.2f} seconds.\n")

# -----------------------
# MAIN LOOP
# -----------------------
if __name__ == "__main__":
    try:
        while True:
            run_master_cycle()
            # Wait 6 hours between full cycles (adjustable)
            time.sleep(6 * 60 * 60)
    except KeyboardInterrupt:
        log_console("🛑 Master Control Loop stopped manually.")
        sys.exit(0)
    except Exception as e:
        log_console(f"❌ Fatal error: {e}")
        sys.exit(1)
