#!/usr/bin/env python3
"""
integration_reporter.py
Hourly log summarizer for Consensus Project

Scans guard/sync logs for anomalies and appends a summary to integration_report.md.
Safe to run under cron or guard loops; never closes the console.

Author: AI Consensus Project
"""

import os
import re
import datetime

# Paths
BASE_DIR = os.path.expanduser("~/consensus-project")
LOG_DIR = os.path.join(BASE_DIR, "memory/logs/system")
REPORT_FILE = os.path.join(LOG_DIR, "integration_report.md")

LOG_FILES = {
    "MCL Guard": os.path.join(LOG_DIR, "mcl_guard.log"),
    "Voice Guard": os.path.join(LOG_DIR, "voice_guard.log"),
    "GitHub Sync": os.path.join(LOG_DIR, "github_sync_launcher.log"),
}

# Patterns for anomaly detection
ERROR_PATTERNS = [
    r"❌",               # explicit failure markers
    r"Error",            # generic error
    r"FAILED",           # uppercase fails
    r"Resource temporarily unavailable",
    r"stale",            # heartbeat stale
]

def scan_log(file_path):
    """Return list of anomaly lines from the given log file."""
    if not os.path.exists(file_path):
        return [f"(no log file found: {file_path})"]

    anomalies = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Look only at last 200 lines for brevity
        for line in lines[-200:]:
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in ERROR_PATTERNS):
                anomalies.append(line.strip())
    except Exception as e:
        anomalies.append(f"(error reading log {file_path}: {e})")

    return anomalies or ["No anomalies detected."]

def write_report():
    """Write the hourly summary report to integration_report.md"""
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## Integration Report {now}\n")
        for name, path in LOG_FILES.items():
            f.write(f"\n### {name} ({os.path.basename(path)})\n")
            anomalies = scan_log(path)
            for line in anomalies:
                f.write(f"- {line}\n")

def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    write_report()
    print(f"[{datetime.datetime.utcnow().isoformat()}Z] ✅ Integration report written to {REPORT_FILE}")

if __name__ == "__main__":
    main()
