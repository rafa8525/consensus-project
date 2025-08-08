
#!/usr/bin/env python3

import subprocess
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_task(command, task_name):
    log(f"Starting task: {task_name}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        log(f"Task succeeded: {task_name}")
    except subprocess.CalledProcessError as e:
        log(f"Task failed: {task_name}")
        log(e.stderr)

if __name__ == "__main__":
    tasks = [
        # Removed: ["python3", "/home/rafa1215/consensus-project/daily_sms_and_push.py"],
        ["python3", "/home/rafa1215/consensus-project/auto_git_sync.py"],
        ["python3", "/home/rafa1215/consensus-project/heartbeat_logger.py"],
        ["python3", "/home/rafa1215/consensus-project/watchdog_log_checker.py"],
        ["python3", "/home/rafa1215/consensus-project/memory/tools/security_audit_runner.py"],
        ["python3", "/home/rafa1215/consensus-project/memory/tools/watchdog_weekly_alert.py"]
    ]

    for task in tasks:
        run_task(task, task[-1].split("/")[-1])
