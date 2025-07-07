import os
import subprocess
from datetime import datetime

# Paths
REPO_PATH = "/home/YOUR_USERNAME/consensus-project"
FILE_PATH = os.path.join(REPO_PATH, "memory", "centralized_knowledge_base.txt")
LOG_PATH = os.path.join(REPO_PATH, "logs", "system", "knowledge_commit_log.txt")
MARKER_PATH = os.path.join(REPO_PATH, ".last_commit_marker.txt")

def get_last_modified_time(path):
    return os.path.getmtime(path)

def get_marker():
    try:
        with open(MARKER_PATH, "r") as f:
            return float(f.read().strip())
    except:
        return 0.0

def update_marker(mod_time):
    with open(MARKER_PATH, "w") as f:
        f.write(str(mod_time))

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
    mod_time = get_last_modified_time(FILE_PATH)
    last_time = get_marker()
    if mod_time != last_time:
        commit_and_push()
        update_marker(mod_time)