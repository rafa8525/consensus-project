#!/usr/bin/env python3
import os
import time
import datetime
import sys

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = "/home/rafa1215/consensus-project"
LOGS_DIR = os.path.join(BASE_DIR, "memory/logs")
HEARTBEAT_LOG = os.path.join(LOGS_DIR, "heartbeat/heartbeat.log")
HEALTH_REPORT = os.path.join(LOGS_DIR, "system/log_health_report.md")
WATCHDOG_LOG = os.path.join(LOGS_DIR, "system/watchdog_alerts.log")

# -------------------------------------------------
# Settings
# -------------------------------------------------
HEARTBEAT_INTERVAL = 3600   # 1 hour between heartbeats when standalone
STALE_THRESHOLD_HOURS = 48  # logs older than 48h = stale

# -------------------------------------------------
# Core functions
# -------------------------------------------------
def write_heartbeat():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(HEARTBEAT_LOG), exist_ok=True)
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(f"[{now}] Heartbeat OK\n")

def get_latest_timestamp(path):
    try:
        files = [os.path.join(path, f) for f in os.listdir(path)]
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            return None
        latest = max(os.path.getmtime(f) for f in files)
        return datetime.datetime.fromtimestamp(latest)
    except Exception:
        return None

def log_watchdog_alert(folder, last_update):
    """Write a placeholder SMS alert for the Watchdog agent."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert = (
        f"[{now}] SMS_ALERT_READY: Log folder '{folder}' is stale "
        f"(last update {last_update.strftime('%Y-%m-%d %H:%M:%S')}).\n"
    )
    os.makedirs(os.path.dirname(WATCHDOG_LOG), exist_ok=True)
    with open(WATCHDOG_LOG, "a") as f:
        f.write(alert)
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(alert)

def run_health_check():
    now = datetime.datetime.now()
    report_lines = [
        f"# Log Health Report\nGenerated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
    ]
    stale_found = False

    for sub in sorted(os.listdir(LOGS_DIR)):
        sub_path = os.path.join(LOGS_DIR, sub)
        if not os.path.isdir(sub_path):
            continue

        latest = get_latest_timestamp(sub_path)
        if latest is None:
            status = "❌ Missing (empty)"
        else:
            age_hours = (now - latest).total_seconds() / 3600
            if age_hours <= STALE_THRESHOLD_HOURS:
                status = f"✅ Fresh (last update {latest.strftime('%Y-%m-%d %H:%M:%S')})"
            else:
                status = f"⚠️ Stale (last update {latest.strftime('%Y-%m-%d %H:%M:%S')})"
                stale_found = True
                log_watchdog_alert(sub, latest)

        report_lines.append(f"- **{sub}/** → {status}")

    os.makedirs(os.path.dirname(HEALTH_REPORT), exist_ok=True)
    with open(HEALTH_REPORT, "w") as f:
        f.write("\n".join(report_lines) + "\n")

    if stale_found:
        with open(HEARTBEAT_LOG, "a") as f:
            f.write(
                f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Log health check found stale entries. See {HEALTH_REPORT}\n"
            )

def run_once():
    write_heartbeat()
    run_health_check()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
        return
    while True:
        run_once()
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
