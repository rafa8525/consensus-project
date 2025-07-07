import os
import time
import subprocess
from datetime import datetime

# Paths
REPO_PATH = "C:/Users/rlymp/consensus-project"
FILE_PATH = os.path.join(REPO_PATH, "memory", "centralized_knowledge_base.txt")
LOG_PATH = os.path.join(REPO_PATH, "logs", "system", "knowledge_commit_log.txt")

# Time between checks (seconds)
CHECK_INTERVAL = 60

def get_last_modified_time(path):
    return os.path.getmtime(path)

def log(message):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

def commit_and_push():
    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", FILE_PATH], check=True)
    commit_msg = f"Auto-commit: Knowledge base update {datetime.now()}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push", "origin", "v1.1-dev"], check=True)
    log(commit_msg)

if __name__ == "__main__":
    print("📡 Watching for changes to centralized_knowledge_base.txt...")
    last_modified = get_last_modified_time(FILE_PATH)
    while True:
        time.sleep(CHECK_INTERVAL)
        current_modified = get_last_modified_time(FILE_PATH)
        if current_modified != last_modified:
            commit_and_push()
            last_modified = current_modified
