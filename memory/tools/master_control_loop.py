#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import subprocess
import threading
import json
from pathlib import Path
from twilio.rest import Client

# ===== SAFE IMPORT: DRIVE POLLER =====
try:
    from drive_poller import poll_drive_and_absorb
except ImportError:
    def poll_drive_and_absorb():
        print("[SYNC] Google Drive sync skipped — drive_poller.py not implemented yet")

# ===== CONFIG =====
TOOLS_DIR = "/home/rafa1215/consensus-project/memory/tools"
MEMORY_DIR = "/home/rafa1215/consensus-project/memory"
LOG_FILE = "/home/rafa1215/consensus-project/memory/logs/agents/master_control.log"
REMINDER_FILE = Path(MEMORY_DIR) / "config" / "reminders.json"
REMINDER_LOG_FILE = Path(MEMORY_DIR) / "logs" / "sms_sent_today.log"

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE")
TWILIO_TO = os.getenv("TWILIO_TO")
client = Client(TWILIO_SID, TWILIO_AUTH)

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ===== LOGGING =====
def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ===== GENERIC SCRIPT RUNNER =====
def run_script(script_name):
    script_path = os.path.join(TOOLS_DIR, script_name)
    if not os.path.exists(script_path):
        log(f"[WARN] Script not found: {script_name}")
        return
    try:
        subprocess.run(["python3", script_path], check=True)
        log(f"[OK] {script_name}")
    except subprocess.CalledProcessError as e:
        log(f"[ERROR] {script_name}: {e}")

# ===== MEMORY FOLDER AUTO-SYNC =====
def auto_memory_sync():
    try:
        subprocess.run(["python3", os.path.join(TOOLS_DIR, "auto_memory_sync.py")], check=False)
        log("[OK] Memory folder sync complete")
    except Exception as e:
        log(f"[ERROR] Memory folder sync: {e}")

# ===== GITHUB SELF-HEAL =====
def github_self_heal():
    try:
        subprocess.run(["python3", os.path.join(TOOLS_DIR, "log_github_heartbeat.py")], check=False)
        subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "push", "origin", "v1.1-dev"], check=False)
        log("[OK] GitHub sync self-heal complete")
    except Exception as e:
        log(f"[ERROR] GitHub self-heal: {e}")

# ===== VOICE TRIGGER SMS SELF-HEAL =====
def voice_trigger_self_heal():
    try:
        subprocess.run(["python3", os.path.join(TOOLS_DIR, "send_reminder.py")], check=False)
        log("[OK] Voice trigger fallback SMS sent")
    except Exception as e:
        log(f"[ERROR] Voice trigger self-heal: {e}")

# ===== VPN SELF-HEAL =====
def vpn_self_heal():
    try:
        subprocess.run(["python3", os.path.join(TOOLS_DIR, "log_vpn_heartbeat.py")], check=False)
        log("[OK] VPN self-heal complete")
    except Exception as e:
        log(f"[ERROR] VPN self-heal: {e}")

# ===== SKIPPED TASK RECOVERY =====
def skipped_task_recovery():
    TASKS = [
        ("VPN Test", "log_vpn_heartbeat.py"),
        ("GitHub Sync", "log_github_heartbeat.py"),
        ("Fitness Log", "log_fitness_heartbeat.py"),
    ]
    for name, script in TASKS:
        try:
            subprocess.run(["python3", os.path.join(TOOLS_DIR, script)], check=False)
            log(f"[OK] Skipped task recovery: {name}")
        except Exception as e:
            log(f"[ERROR] Skipped task recovery ({name}): {e}")

# ===== DRIVE SYNC =====
def run_drive_sync():
    log("[SYNC] Polling Google Drive...")
    try:
        poll_drive_and_absorb()
        log("[SYNC] Drive poll completed successfully")
    except Exception as e:
        log(f"[SYNC ERROR] {e}")

# ===== DIRECT GIT COMMIT & PUSH =====
def run_github_commit():
    log("[GIT] Committing memory to GitHub...")
    try:
        subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "add", "."], check=False)
        commit = subprocess.run(
            ["git", "-C", "/home/rafa1215/consensus-project", "commit", "-m", "Automated commit"],
            capture_output=True,
            text=True
        )
        if "nothing to commit" in commit.stdout.lower() or "nothing to commit" in commit.stderr.lower():
            log("[GIT] No changes to commit — skipping")
        else:
            subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "push", "origin", "v1.1-dev"], check=False)
            log("[GIT] Git commit & push complete")
    except Exception as e:
        log(f"[GIT ERROR] {e}")

# ===== REMINDERS =====
def load_reminders():
    try:
        with open(REMINDER_FILE) as f:
            data = json.load(f)
        return data.get("reminders", [])
    except Exception as e:
        log(f"[REMINDER] Failed to load reminders.json: {e}")
        return []

def load_sent_today():
    if not REMINDER_LOG_FILE.exists():
        return set()
    today = datetime.date.today().isoformat()
    sent = set()
    with open(REMINDER_LOG_FILE) as f:
        for line in f:
            if line.startswith(today):
                sent.add(line.strip().split("|")[1])
    return sent

def log_sent(message):
    with open(REMINDER_LOG_FILE, "a") as f:
        f.write(f"{datetime.date.today().isoformat()}|{message}\n")

def send_sms(message):
    try:
        client.messages.create(body=message, from_=TWILIO_FROM, to=TWILIO_TO)
        log(f"[REMINDER SENT] {message}")
        log_sent(message)
    except Exception as e:
        log(f"[REMINDER ERROR] {e}")

def matches_now(reminder):
    now = datetime.datetime.now()
    reminder_time = reminder.get("time")
    day = reminder.get("day", None)
    interval_days = reminder.get("interval_days", None)
    if day and now.strftime("%A") != day:
        return False
    if reminder_time and now.strftime("%H:%M") != reminder_time:
        return False
    if interval_days:
        days_since_epoch = (now.date() - datetime.date(1970, 1, 1)).days
        if days_since_epoch % interval_days != 0:
            return False
    return True

def run_reminder_check():
    reminders = load_reminders()
    sent_today = load_sent_today()
    for reminder in reminders:
        message = reminder["message"]
        if matches_now(reminder) and message not in sent_today:
            send_sms(message)

# ===== MAIN LOOP =====
def main():
    log("=== Master Control Loop Started (10 min interval) ===")
    while True:
        threads = []
        # Heartbeats
        for hb in [
            "log_github_heartbeat.py",
            "log_vpn_heartbeat.py",
            "log_sms_heartbeat.py",
            "log_perplexity_heartbeat.py",
            "log_fitness_heartbeat.py",
            "log_geofence_heartbeat.py",
            "log_voice_reminder_heartbeat.py"
        ]:
            threads.append(threading.Thread(target=run_script, args=(hb,)))

        # Self-healing & recovery
        threads.append(threading.Thread(target=github_self_heal))
        threads.append(threading.Thread(target=voice_trigger_self_heal))
        threads.append(threading.Thread(target=vpn_self_heal))
        threads.append(threading.Thread(target=skipped_task_recovery))
        threads.append(threading.Thread(target=auto_memory_sync))

        # Maintenance
        threads.append(threading.Thread(target=run_drive_sync))
        threads.append(threading.Thread(target=run_github_commit))

        # Reminders
        threads.append(threading.Thread(target=run_reminder_check))

        # Start & wait for all threads
        for t in threads: t.start()
        for t in threads: t.join()

        # Push logs
        try:
            subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "add", LOG_FILE], check=False)
            subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "commit", "-m", "Update master control log"], check=False)
            subprocess.run(["git", "-C", "/home/rafa1215/consensus-project", "push", "origin", "v1.1-dev"], check=False)
            log("[OK] Logs pushed to GitHub")
        except Exception as e:
            log(f"[ERROR] Pushing logs to GitHub: {e}")

        time.sleep(600)  # 10 minutes

if __name__ == "__main__":
    main()
