#!/usr/bin/env python3
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def run_task(command, task_name):
    try:
        logging.info(f"Starting task: {task_name}")
        subprocess.run(command, check=True)
        logging.info(f"Task succeeded: {task_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Task failed ({task_name}): {e}")

if __name__ == "__main__":
    run_task(["python3", "/home/rafa1215/consensus-project/daily_sms_and_push.py"], "Daily SMS and Push")
    run_task(["python3", "/home/rafa1215/consensus-project/auto_git_sync.py"], "Auto Git Sync")
    run_task(["python3", "/home/rafa1215/heartbeat_logger.py"], "Heartbeat Logger")
