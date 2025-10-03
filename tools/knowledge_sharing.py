#!/usr/bin/env python3
import os, datetime, json

# Paths
BASE_DIR = "/home/rafa1215/consensus-project/memory/centralized_knowledge_base"
LOG_DIR = "/home/rafa1215/consensus-project/memory/logs/system"
REPORT_DIR = "/home/rafa1215/consensus-project/memory/logs/progress"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

BUS_FILE = os.path.join(BASE_DIR, "knowledge_bus.md")
SUMMARY_FILE = os.path.join(REPORT_DIR, "knowledge_sharing_summary.md")
HEARTBEAT_FILE = os.path.join(LOG_DIR, "heartbeat.md")

def log_heartbeat(msg: str):
    """Append a knowledge sharing entry to heartbeat.md"""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"{timestamp} KNOWLEDGE-SHARE: {msg}\n")

def publish_skill(agent: str, description: str):
    """Publish a new skill update to the knowledge bus"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} — {agent} exported {description}\n"
    with open(BUS_FILE, "a") as f:
        f.write(entry)
    log_heartbeat(f"{agent} shared {description}")

def summarize_weekly():
    """Generate a weekly summary of all knowledge sharing"""
    if not os.path.exists(BUS_FILE):
        return

    with open(BUS_FILE, "r") as f:
        lines = f.readlines()

    week = datetime.datetime.now().strftime("%Y-%m-%d")
    summary = [f"## Weekly Knowledge Summary — {week}\n"]
    summary.extend([f"- {line.strip()}" for line in lines[-10:]])  # last 10 events

    with open(SUMMARY_FILE, "w") as f:
        f.write("\n".join(summary) + "\n")

def export_skill(agent: str, skill_data: dict, skill_file: str):
    """
    Store a reusable skill (logic/config) in JSON format.
    Example: VPN Runner detection logic, Fitness calorie conversion, etc.
    """
    path = os.path.join(BASE_DIR, f"{skill_file}.json")
    with open(path, "w") as f:
        json.dump(skill_data, f, indent=2)
    publish_skill(agent, f"skill → {skill_file}.json")

# ------------------------------------------------------------------
# Demo execution when run directly
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Example publishing
    publish_skill("vpn_runner", "improved IP check function")
    publish_skill("fitness_integration", "calorie → step conversion method")

    # Example exporting structured skill
    export_skill("reminder_master", {"pattern": "weekly nudges", "method": "SMS+voice"}, "reminder_pattern")

    # Generate summary
    summarize_weekly()
    print("✅ Knowledge sharing updates recorded.")
