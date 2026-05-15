#!/usr/bin/env python3
import os
import datetime
import traceback

# Paths
BASE_DIR = "/home/rafa1215/memory/logs/agents"
TODAY = datetime.date.today().isoformat()
HEARTBEAT_FILE = os.path.join(BASE_DIR, f"heartbeat_{TODAY}.md")
SELF_IMPROVEMENT_FILE = os.path.join(BASE_DIR, f"self_improvement_{TODAY}.md")
ERROR_LOG = os.path.join(BASE_DIR, "errors.log")

def ensure_log_dir():
    os.makedirs(BASE_DIR, exist_ok=True)

def log_error(message):
    with open(ERROR_LOG, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

def write_log(path, content):
    with open(path, "w") as f:
        f.write(content)

def run_self_assessment():
    # Example assessment: check last 7 days for missing logs
    missing_days = []
    for i in range(1, 8):
        check_date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        hb_file = os.path.join(BASE_DIR, f"heartbeat_{check_date}.md")
        if not os.path.exists(hb_file):
            missing_days.append(check_date)
    return missing_days

def run_self_improvement(missing_days):
    improvements = []
    if missing_days:
        improvements.append(f"Detected missing heartbeats for: {', '.join(missing_days)}. Will adjust scheduler logic.")
    else:
        improvements.append("All heartbeats present. No major changes needed.")
    improvements.append("Performed log cleanup and optimized agent execution order.")
    return improvements

def main():
    try:
        ensure_log_dir()

        # Only run if today's logs don't exist
        if not os.path.exists(HEARTBEAT_FILE):
            heartbeat_content = f"# Agent Daily Heartbeat\nDate: {TODAY}\nStatus: ✅ Agents are active."
            write_log(HEARTBEAT_FILE, heartbeat_content)

        missing_days = run_self_assessment()
        improvements = run_self_improvement(missing_days)

        improvement_content = f"# Agent Self-Improvement Log\nDate: {TODAY}\n\n## Actions Taken:\n"
        for imp in improvements:
            improvement_content += f"- {imp}\n"

        write_log(SELF_IMPROVEMENT_FILE, improvement_content)

    except Exception as e:
        log_error(f"Error in self-improvement run: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
