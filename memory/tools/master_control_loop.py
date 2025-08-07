#!/usr/bin/env python3
import subprocess
import time
import logging
from datetime import datetime

LOG_PATH = "/home/rafa1215/consensus-project/memory/logs/agents/master_control.log"
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(message)s")

def run_task(name, command):
    logging.info(f"Starting task: {name}")
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Task succeeded: {name}")
        logging.debug(f"{name} output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Task failed: {name}")
        logging.error(f"{e.stderr.strip()}")

def main_loop():
    logging.info("=== Master Control Loop Started (5 sec interval) ===")

    # Core daily heartbeat loggers
    run_task("Heartbeat Logger", "python3 /home/rafa1215/consensus-project/memory/tools/heartbeat_logger.py")
    run_task("GitHub Heartbeat", "python3 /home/rafa1215/consensus-project/memory/tools/log_github_heartbeat.py")
    run_task("Perplexity Heartbeat", "python3 /home/rafa1215/consensus-project/memory/tools/log_perplexity_heartbeat.py")
    run_task("SMS Reminder Tester", "python3 /home/rafa1215/consensus-project/simulate_sms_test.py")

    # Watchdog weekly alert (runs daily but only triggers on Sunday)
    run_task("Watchdog Weekly Alert", "python3 /home/rafa1215/consensus-project/memory/tools/watchdog_weekly_alert.py")

    # Weekly status PDF generator (also Sunday-only)
    run_task("Weekly Log Summary", "python3 /home/rafa1215/reminder-api/generate_weekly_log_summary.py")

    # 🔐 Security audit
    run_task("Security Audit", "python3 /home/rafa1215/consensus-project/memory/tools/security_audit_runner.py")

    # Optional simulations (if activated)
    run_task("Simulation Engine", "python3 /home/rafa1215/consensus-project/memory/tools/run_simulation_suite.py")

if __name__ == "__main__":
    main_loop()
