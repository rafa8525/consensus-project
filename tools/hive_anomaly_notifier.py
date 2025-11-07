#!/usr/bin/env python3
"""
hive_anomaly_notifier.py
------------------------------------------------------------
Scans recent logs for anomalies (failed agents, <5% improvement,
VPN/security issues) and sends an SMS only if an anomaly is found.
------------------------------------------------------------
"""

import os, re
from datetime import datetime, timezone
from twilio.rest import Client

# === Twilio config (verified October 27) ===
ACCOUNT_SID = "AC4b4d18bdc5bc1b13f7bf2220a9d02287"
AUTH_TOKEN   = "3cd125fe97e04a2203ea7e24c6e9f4d8"
FROM_NUMBER  = "+18886607830"
TO_NUMBER    = "+16502283267"

# === Paths ===
LOG_DIR = os.path.expanduser("~/memory/logs/system")
EVOL_LOG = os.path.join(LOG_DIR, "evolution_auditor.log")
VPN_LOG  = os.path.join(LOG_DIR, "vpn_test_runner.log")
HIVE_LOG = os.path.join(LOG_DIR, "hive_mother.log")
NOTIFY_LOG = os.path.join(LOG_DIR, "hive_anomaly_notifier.log")

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg):
    line = f"[{timestamp()}] {msg}\n"
    os.makedirs(os.path.dirname(NOTIFY_LOG), exist_ok=True)
    with open(NOTIFY_LOG, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def scan_file(path, patterns):
    """Return matching lines if any pattern is found."""
    if not os.path.exists(path):
        return []
    matches = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for p in patterns:
                if re.search(p, line, re.IGNORECASE):
                    matches.append(line.strip())
    return matches

def detect_anomalies():
    issues = []
    evol_patterns = [r"below\s+5\.0%", r"need retraining", r"error", r"fail"]
    vpn_patterns  = [r"VPN.*fail", r"error", r"disconnected"]
    hive_patterns = [r"ERROR", r"fail", r"missing agent", r"0/55"]
    issues += scan_file(EVOL_LOG, evol_patterns)
    issues += scan_file(VPN_LOG, vpn_patterns)
    issues += scan_file(HIVE_LOG, hive_patterns)
    return issues

def send_sms(body):
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        msg = client.messages.create(body=body, from_=FROM_NUMBER, to=TO_NUMBER)
        log(f"📱 SMS sent (SID: {msg.sid}) → {TO_NUMBER}")
    except Exception as e:
        log(f"[ERROR] Failed to send SMS: {e}")

def main():
    log("=== Hive Anomaly Notifier: Begin ===")
    issues = detect_anomalies()
    if issues:
        summary = "\n".join(issues[-5:])  # last few lines only
        body = f"⚠️ Hive Mother Alert ({timestamp()}):\n{summary}"
        send_sms(body)
        log(f"Anomalies detected → notification sent.")
    else:
        log("No anomalies detected; no SMS sent.")
    log("=== Hive Anomaly Notifier: Complete ===\n")

if __name__ == "__main__":
    main()
