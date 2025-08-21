#!/usr/bin/env python3
import os
import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Memory Watchdog ===
class MemoryAbsorbHandler(FileSystemEventHandler):
    def __init__(self, absorb_cmd):
        super().__init__()
        self.absorb_cmd = absorb_cmd

    def on_created(self, event):
        if not event.is_directory:
            subprocess.Popen(self.absorb_cmd, shell=True)

    def on_modified(self, event):
        if not event.is_directory:
            subprocess.Popen(self.absorb_cmd, shell=True)

def start_memory_watcher():
    memory_path = os.path.expanduser("~/consensus-project/memory")
    absorb_cmd = "/usr/bin/python3 ~/consensus-project/tools/absorb_runner.py && /usr/bin/python3 ~/consensus-project/tools/absorb_log_append.py auto"
    event_handler = MemoryAbsorbHandler(absorb_cmd)
    observer = Observer()
    observer.schedule(event_handler, memory_path, recursive=True)
    observer.start()
    print(f"[{datetime.now()}] INFO: Watching '{memory_path}' for changes...")
    return observer

# === Task Definitions ===
TASKS = [
    {
        "name": "Daily SMS and Push",
        "script": "/home/rafa1215/consensus-project/daily_sms_and_push.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/agents/daily_sms_and_push.log"
    },
    {
        "name": "Auto Git Sync",
        "script": "/home/rafa1215/consensus-project/auto_git_sync.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/git/git_sync_log.txt"
    },
    {
        "name": "Heartbeat Logger",
        "script": "/home/rafa1215/consensus-project/heartbeat_logger.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/heartbeat/heartbeat_log.txt"
    },
    {
        "name": "Watchdog Log Checker",
        "script": "/home/rafa1215/consensus-project/watchdog_log_checker.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/watchdog/failure_log.txt"
    },
    {
        "name": "Security Audit",
        "script": "/home/rafa1215/consensus-project/memory/tools/security_audit_runner.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/security/security_audit_log.txt"
    },
    {
        "name": "Weekly Watchdog Alert",
        "script": "/home/rafa1215/consensus-project/memory/tools/watchdog_weekly_alert.py",
        "log": "/home/rafa1215/consensus-project/memory/logs/watchdog/weekly_alert_log.txt"
    }
]

# Ensure log directories exist
def ensure_log_dirs():
    for task in TASKS:
        log_dir = os.path.dirname(task["log"])
        os.makedirs(log_dir, exist_ok=True)

# Execute a single task and log result
def run_task(task):
    try:
        result = subprocess.run(["python3", task["script"]], capture_output=True, text=True, timeout=120)
        status = "succeeded" if result.returncode == 0 else f"failed (code {result.returncode})"
        log_entry = f"[{datetime.now()}] Task {status}: {task['name']}\n"
        with open(task["log"], "a") as f:
            f.write(log_entry)
        print(f"[INFO] {log_entry.strip()}")
    except Exception as e:
        error_entry = f"[{datetime.now()}] Task exception: {task['name']} - {e}\n"
        with open(task["log"], "a") as f:
            f.write(error_entry)
        print(f"[ERROR] {error_entry.strip()}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] INFO: === Master Control Loop Started ===")
    ensure_log_dirs()

    # Start memory watcher
    observer = start_memory_watcher()

    # Run all tasks once at startup
    for task in TASKS:
        print(f"[{datetime.now()}] INFO: Starting task: {task['name']}")
        run_task(task)

    # Keep process alive (so Always-on task runs forever)
    try:
        while True:
            time.sleep(60)  # idle loop, memory watcher runs in background
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
