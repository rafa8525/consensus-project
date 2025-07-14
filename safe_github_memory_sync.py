import os
import subprocess
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def sync_github_memory():
    log("Starting Git pull from GitHub...")
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd="/home/rafa1215/consensus-project/memory",
            capture_output=True,
            text=True,
            check=True
        )
        log("GitHub memory folder synced.")
        log(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        log("Git pull failed.")
        log(e.stderr.strip())
        return

def index_memory():
    log("Running memory indexer...")
    try:
        result = subprocess.run(
            ["python3", "memory_indexer.py"],
            cwd="/home/rafa1215/reminder-api",
            capture_output=True,
            text=True,
            check=True
        )
        log("Memory indexer completed.")
        log(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        log("Memory indexing failed.")
        log(e.stderr.strip())

def commit_log_updates():
    log("Checking for memory log updates...")
    os.chdir("/home/rafa1215/consensus-project")

    subprocess.run("git add memory/logs/**/*.md", shell=True)

    status = subprocess.run("git diff --cached --quiet", shell=True)
    if status.returncode != 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"🧠 Auto-log sync for {timestamp}"
        subprocess.run(f'git commit -m "{commit_message}"', shell=True)
        subprocess.run("git push origin v1.1-dev", shell=True)
        log("Log changes committed and pushed.")
    else:
        log("No new memory logs to commit.")

if __name__ == "__main__":
    sync_github_memory()
    index_memory()
    commit_log_updates()
    log("✅ GitHub memory sync, indexing, and log push complete.")
