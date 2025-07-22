import os
import subprocess
from datetime import datetime

LOG_FILE = "memory/logs/reminders/github_memory_check_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def run_git_sync():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Stage all Python files and all memory log files recursively
        subprocess.run(["git", "add", "*.py"], check=True)
        subprocess.run(["git", "add", "--all", "memory/logs/"], check=True)

        # Skip commit if nothing changed
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp} — No changes to sync\n")
            return

        # Commit and push
        subprocess.run(["git", "commit", "-m", f"Auto-log sync for {timestamp}"], check=True)
        subprocess.run(["git", "push", "origin", "v1.1-dev"], check=True)

        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} — Git sync successful\n")

    except subprocess.CalledProcessError as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} — Git sync failed: {e}\n")

run_git_sync()
