#!/usr/bin/env python3
import os
import time
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import logging

LOG_FILE = '/home/rafa1215/consensus-project/memory/logs/agents/master_control.log'
os.makedirs(Path(LOG_FILE).parent, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s: %(message)s')

ENV_PATH = Path("/home/rafa1215/consensus-project/.env")
MAX_RESTART_ATTEMPTS = 2
restart_attempts = {}

TASKS = [
    ("Daily SMS & Push", "/home/rafa1215/consensus-project/daily_sms_and_push.py", 86400),
    ("Auto Git Sync", "/home/rafa1215/consensus-project/auto_git_sync.py", 43200),
    # other tasks unchanged ...
]

last_run = {task[0]: 0 for task in TASKS}

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"{ts} {msg}"
    print(entry)
    logging.info(entry)

def load_env():
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
        log(".env loaded successfully.")
    else:
        log(f".env file not found at {ENV_PATH}")
        raise FileNotFoundError(f".env file not found at {ENV_PATH}")

def run_script(path):
    load_env()
    try:
        result = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            env=os.environ
        )
        log(f"[TASK] {os.path.basename(path)} stdout:\n{result.stdout.strip()}")
        if result.stderr.strip():
            log(f"[TASK] {os.path.basename(path)} stderr:\n{result.stderr.strip()}")
        if result.returncode != 0:
            raise Exception(f"Exit code {result.returncode}")
    except Exception as e:
        raise e

def run_with_recovery(name, path):
    try:
        run_script(path)
        restart_attempts[name] = 0
    except Exception as e:
        log(f"[ERROR] {name} failed: {e}")
        restart_attempts[name] = restart_attempts.get(name, 0) + 1
        if restart_attempts[name] <= MAX_RESTART_ATTEMPTS:
            log(f"[RECOVERY] Restarting {name} (Attempt {restart_attempts[name]})")
            try:
                run_script(path)
            except Exception as e2:
                log(f"[RECOVERY ERROR] {name} failed again: {e2}")
        else:
            log(f"[ALERT] {name} failed {restart_attempts[name]} times. Manual intervention needed.")

def main():
    log("=== Master Control Loop Started (10 min interval) ===")
    while True:
        now = time.time()
        for name, path, interval in TASKS:
            if now - last_run[name] >= interval:
                run_with_recovery(name, path)
                last_run[name] = now
        time.sleep(600)

if __name__ == "__main__":
    main()
