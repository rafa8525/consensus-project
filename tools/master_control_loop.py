#!/usr/bin/env python3
"""
master_control_loop.py
------------------------------------------------------------
Master Control Loop v6.0
Coordinates all system subsystems in sequential cycles:
  - Guard + Security Checks
  - VPN & Audit
  - Fitness, Knowledge, Agent Evolution
  - Summary integration
  - 📁 Movie List Watchdog Monitor (parallel thread)
------------------------------------------------------------
Safe to run continuously or via schedule.
------------------------------------------------------------
"""

import os
import subprocess
import time
import datetime
import traceback
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Paths ===
BASE = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.join(BASE, "memory/logs/system")
LOG_FILE = os.path.join(LOG_DIR, "master_control_loop.log")
MOVIE_LOG_PATH = os.path.join(BASE, "logs/file_monitor.log")
MOVIE_LIST_PATH = os.path.join(BASE, "memory/logs/media/movie_list_status.md")
MOVIE_DETECTOR_SCRIPT = os.path.join(BASE, "agents/movie_detector.py")

# === Log Rotation ===
MAX_SIZE_MB = 100
os.makedirs(LOG_DIR, exist_ok=True)
if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_SIZE_MB * 1024 * 1024:
    ts = int(time.time())
    rotated = LOG_FILE.replace(".log", f"_{ts}.log")
    os.rename(LOG_FILE, rotated)
    open(LOG_FILE, "w").close()
    print(f"[{ts}] Rotated master_control_loop.log (> {MAX_SIZE_MB} MB) → {rotated}")

# === Helpers ===
def timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg):
    line = f"[{timestamp()}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_script(script):
    try:
        start = time.time()
        subprocess.run(["python3", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elapsed = round(time.time() - start, 2)
        log(f"✅ Executed {script} successfully ({elapsed}s)")
        return True
    except subprocess.CalledProcessError:
        log(f"❌ Error executing {script}: subprocess error.")
        return False
    except Exception as e:
        log(f"❌ Exception while running {script}: {e}")
        return False

def safe_sleep(seconds):
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        log("⚠️ Interrupted manually.")
        raise

# === Watchdog Thread ===
class MovieListMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("movie_list_status.md"):
            logging.info(f"🎥 Detected change in movie list: {event.src_path}")
            self.trigger_detector()

    def trigger_detector(self):
        try:
            subprocess.run(["python3", MOVIE_DETECTOR_SCRIPT], check=True)
            logging.info("✅ movie_detector.py executed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ movie_detector.py failed: {e}")
        except Exception as e:
            logging.error(f"❌ Exception in watchdog trigger: {e}")

def start_movie_watchdog():
    logging.basicConfig(
        filename=MOVIE_LOG_PATH,
        level=logging.INFO,
        format='%(asctime)s|%(levelname)s|%(message)s'
    )
    observer = Observer()
    handler = MovieListMonitor()
    observer.schedule(handler, path=os.path.dirname(MOVIE_LIST_PATH), recursive=False)
    observer.start()
    logging.info("🎬 Movie List Watchdog Started")
    threading.Thread(target=observer.join, daemon=True).start()

# === Core Workflow ===
def main():
    log("==== Master Control Loop v6.0 (continuous) ====")
    start_movie_watchdog()

    while True:
        try:
            log("==== Master Control Loop Cycle Start ====")

            log("---- Guard Cycle Started ----")
            for tool in [
                "log_repair_guard.py",
                "gmail_refresh_guard_v3.py",
                "calendar_sync_guard_v3.py",
                "master_guard_integrator.py",
            ]:
                run_script(os.path.join(BASE, "tools", tool))
            log("---- Guard Cycle Complete ----")

            log("---- Core Cycle Started ----")
            for tool in [
                "vpn_auto_detect_activate.py",
                "security_audit_runner.py",
                "weekly_status_report.py",
                "progress_evaluation_runner.py",
            ]:
                run_script(os.path.join(BASE, "tools", tool))
            log("---- Core Cycle Complete ----")

            log("---- Fitness Cycle Started ----")
            for tool in [
                "fitness_tracking_verifier.py",
                "backup_fitness.py",
            ]:
                run_script(os.path.join(BASE, "tools", tool))
            log("---- Fitness Cycle Complete ----")

            log("---- Knowledge/Reports Cycle Started ----")
            for tool in [
                "knowledge_sharing_validator.py",
                "status_report_builder.py",
            ]:
                run_script(os.path.join(BASE, "tools", tool))
            log("---- Knowledge/Reports Cycle Complete ----")

            log("---- Agent Evolution/Repair Cycle Started ----")
            for tool in [
                "agent_evolution_cycle.py",
                "agent_self_repair_loop.py",
            ]:
                run_script(os.path.join(BASE, "tools", tool))
            log("---- Agent Evolution/Repair Cycle Complete ----")

            log("---- Hive Mother Summary Integration ----")
            run_script(os.path.join(BASE, "tools", "hive_summary_integrator.py"))
            run_script(os.path.join(BASE, "tools", "hive_anomaly_watcher.py"))
            log("---- Hive Mother Summary Cycle Complete ----")

            log("✅ All subsystems executed successfully.")
            log("==== Master Control Loop Cycle Complete ====")

        except Exception as e:
            log("⚠️ Unhandled exception in Master Control Loop.")
            log(traceback.format_exc())

        safe_sleep(60)

# === Entry Point ===
if __name__ == "__main__":
    main()
