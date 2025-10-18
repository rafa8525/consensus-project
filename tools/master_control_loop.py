#!/usr/bin/env python3
"""
master_control_loop.py
AI Consensus System – Master Control Loop (v1.2)
Handles scheduling, agent execution, and voice command routing.

New in this version:
- Gmail Agent auto-scheduler (every 30 min)
- Voice triggers for Gmail (check, summarize, read aloud)
- Integrated voice reader for top Gmail summaries
- Modular design for future agents (VPN, Fitness, SMS alerts)
"""

import os
import sys
import time
import json
import datetime
import subprocess
import traceback

# === CORE PATHS ===
BASE_DIR = os.path.expanduser("~/consensus-project")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
LOG_DIR = os.path.join(BASE_DIR, "memory", "logs", "system")
VOICE_CONFIG = os.path.join(BASE_DIR, "config", "voice_triggers.yaml")
HEARTBEAT_FILE = os.path.join(LOG_DIR, "heartbeat_master.log")

os.makedirs(LOG_DIR, exist_ok=True)

# === LOGGING ===
def log(msg: str):
    """Write timestamped message to heartbeat_master.log."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(HEARTBEAT_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

# === AGENT EXECUTION ===
def run_agent(script_path: str):
    """Safely execute an agent and log results."""
    try:
        log(f"Running agent: {script_path}")
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            log(f"✅ Agent completed successfully: {script_path}")
            if result.stdout.strip():
                log(result.stdout.strip())
        else:
            log(f"❌ Agent failed ({result.returncode}): {script_path}")
            if result.stderr.strip():
                log(result.stderr.strip())
    except Exception as e:
        log(f"⚠️ Exception while running agent {script_path}: {e}")
        traceback.print_exc()

# === LOAD VOICE TRIGGERS ===
def load_voice_triggers():
    """Load YAML-style voice trigger configuration."""
    if not os.path.exists(VOICE_CONFIG):
        return {}
    triggers = {}
    try:
        with open(VOICE_CONFIG, "r", encoding="utf-8") as f:
            for line in f:
                if "phrase:" in line:
                    phrase = line.split("phrase:")[1].strip().strip('"').strip("'")
                elif "action:" in line:
                    action = line.split("action:")[1].strip().strip('"').strip("'")
                    triggers[phrase.lower()] = action
        return triggers
    except Exception as e:
        log(f"Error loading voice_triggers.yaml: {e}")
        return {}

# === DEFAULT VOICE TRIGGERS ===
VOICE_TRIGGERS_DEFAULT = {
    "check my gmail": f"python3 {AGENTS_DIR}/gmail_agent.py",
    "summarize unread messages": f"python3 {AGENTS_DIR}/gmail_agent.py",
    "read my gmail": f"python3 {AGENTS_DIR}/gmail_voice_reader.py",
}

# === HEARTBEAT LOOP ===
def main_loop():
    log("=== Master Control Loop v1.2 started ===")

    # Load triggers (YAML file overrides defaults)
    voice_triggers = load_voice_triggers() or VOICE_TRIGGERS_DEFAULT
    for phrase, action in voice_triggers.items():
        log(f"Voice trigger loaded: '{phrase}' → {action}")

    # Define agent paths
    gmail_agent = os.path.join(AGENTS_DIR, "gmail_agent.py")
    gmail_reader = os.path.join(AGENTS_DIR, "gmail_voice_reader.py")

    # Master loop
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            log(f"--- Master heartbeat cycle #{cycle_count} ---")

            # Scheduled Gmail Agent (every 30 minutes)
            if cycle_count % 1 == 0:  # every cycle = 30 min by default
                if os.path.exists(gmail_agent):
                    log("⏱ Running scheduled Gmail Agent...")
                    run_agent(gmail_agent)
                else:
                    log("⚠️ Gmail Agent script not found.")

            # Example of voice-trigger simulation placeholder:
            # This could later tie to Pixel Watch, mic input, or Twilio voice.
            # In production, voice phrases trigger via event listener.

            # Sleep 30 minutes between cycles
            log("Master loop sleeping for 30 minutes...")
            time.sleep(1800)

        except KeyboardInterrupt:
            log("🛑 Master Control Loop interrupted manually.")
            break
        except Exception as e:
            log(f"Unexpected error in Master Control Loop: {e}")
            traceback.print_exc()
            time.sleep(60)

    log("=== Master Control Loop stopped ===")

# === ENTRY POINT ===
if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        log(f"Fatal error in Master Control Loop: {e}")
        traceback.print_exc()
        sys.exit(1)
