#!/usr/bin/env python3
"""
hive_anomaly_watcher.py  —  Log-only Version
------------------------------------------------------------
Scans Hive Mother daily summary for anomalies and low confidence
levels in predictive analytics.

✔ No email sending
✔ Writes findings to ~/memory/logs/system/hive_anomaly_watcher.log
✔ Safe to run hourly or daily — never sends Gmail
------------------------------------------------------------
"""

import os
import re
from datetime import datetime, timezone

# === Paths ===
LOG_PATH = os.path.expanduser("~/memory/logs/system/hive_summary.log")
WATCHER_LOG = os.path.expanduser("~/memory/logs/system/hive_anomaly_watcher.log")

# === Thresholds ===
CONF_THRESHOLD = 50.0
RISK_THRESHOLD = 10.0

# === Utilities ===
def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg):
    os.makedirs(os.path.dirname(WATCHER_LOG), exist_ok=True)
    with open(WATCHER_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp()}] {msg}\n")
    print(msg)

# === Core Logic ===
def parse_confidence_and_risk():
    """Extract predictive confidence and risk from the latest summary."""
    if not os.path.exists(LOG_PATH):
        log("❌ Hive summary log not found.")
        return None, None

    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    sections = re.findall(r"--- Predictive Summary ---([\s\S]+?)Summary compiled successfully", content)
    if not sections:
        log("⚠️ No predictive summary section found.")
        return None, None

    latest = sections[-1]
    conf_match = re.search(r"Confidence=([0-9.]+)%", latest)
    risk_match = re.search(r"Risk=([0-9.]+)%", latest)

    conf = float(conf_match.group(1)) if conf_match else None
    risk = float(risk_match.group(1)) if risk_match else None

    log(f"🔍 Extracted Confidence={conf} | Risk={risk}")
    return conf, risk

def report_anomaly(conf, risk):
    """Log anomaly details only (no email)."""
    body = (
        f"Anomaly detected at {timestamp()}.\n"
        f"Predictive Confidence: {conf}%\n"
        f"Risk Level: {risk}%\n"
        f"Thresholds — Confidence<{CONF_THRESHOLD}, Risk>{RISK_THRESHOLD}\n"
        f"Action: Review predictive logs and rerun predictive agents.\n"
    )
    log(f"⚠️ {body}")

# === Main ===
def main():
    log("=== Hive Anomaly Watcher: Begin ===")
    conf, risk = parse_confidence_and_risk()
    if conf is None:
        log("No data to analyze; exiting.")
        return

    if conf < CONF_THRESHOLD or (risk is not None and risk > RISK_THRESHOLD):
        report_anomaly(conf, risk)
    else:
        log(f"✅ All clear — Confidence={conf}%, Risk={risk}%")

    log("=== Hive Anomaly Watcher: Complete ===")

if __name__ == "__main__":
    main()
