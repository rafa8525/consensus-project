#!/usr/bin/env python3
import subprocess
import time
import logging
from datetime import datetime

LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/agents/master_control.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    filemode='a'
)

def run_task(command, task_name, cwd=None):
    try:
        logging.info(f"Starting task: {task_name}")
        subprocess.run(command, check=True, cwd=cwd)
        logging.info(f"Task succeeded: {task_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Task failed ({task_name}): {e}")

def main():
    last_heartbeat = None
    heartbeat_interval = 600  # 10 minutes in seconds

    while True:
        now = datetime.now()

        # Task 1: daily_sms_and_push.py (run once daily at 9:00 AM)
        if now.hour == 9 and now.minute == 0:
            run_task(
                ["python3", "/home/rafa1215/consensus-project/daily_sms_and_push.py"],
                "Daily SMS and Push"
            )

        # Task 2: auto_git_sync.py (run every hour at minute 0)
        if now.minute == 0:
            run_task(
                ["python3", "/home/rafa1215/consensus-project/auto_git_sync.py"],
                "Auto Git Sync",
                cwd="/home/rafa1215/consensus-project"
            )

        # Task 3: heartbeat_logger.py (run every 10 minutes)
        if last_heartbeat is None or (time.time() - last_heartbeat) >= heartbeat_interval:
            run_task(
                ["python3", "/home/rafa1215/heartbeat_logger.py"],
                "Heartbeat Logger"
            )
            last_heartbeat = time.time()

        time.sleep(30)

if __name__ == "__main__":
    logging.info("=== Master Control Loop Started ===")
    main()
