#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load .env values
load_dotenv("/home/rafa1215/consensus-project/.env")

# Constants
REPO_DIR = "/home/rafa1215/consensus-project"
LOG_DIR = os.path.join(REPO_DIR, "memory/logs/git")
LOG_FILE = os.path.join(LOG_DIR, "git_sync_log.txt")

def write_log(message):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")

def run_git_sync():
    try:
        write_log("=== Git sync started ===")
        os.chdir(REPO_DIR)

        subprocess.run(["git", "pull"], check=True)
        write_log("Git pull completed.")

        subprocess.run(["git", "add", "."], check=True)
        write_log("Git add completed.")

        commit_msg = f"Auto-log sync for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        write_log(f"Git commit done: {commit_msg}")

        subprocess.run(["git", "push"], check=True)
        write_log("Git push completed.")
        write_log("=== Git sync successful ===")

    except subprocess.CalledProcessError as e:
        write_log(f"ERROR: Git command failed: {e}")
    except Exception as e:
        write_log(f"ERROR: {str(e)}")

if __name__ == "__main__":
    run_git_sync()
