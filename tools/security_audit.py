#!/usr/bin/env python3
"""
security_audit.py
Phase 4: Security Hardening

Purpose:
- Run daily security checks on the project environment.
- File permission audit (detect world-writable files).
- Package audit (check outdated or vulnerable packages).
- Credential audit (scan logs/code for exposed secrets).
"""

import os
import datetime
import subprocess
from pathlib import Path
import re

BASE_DIR = Path("/home/rafa1215/consensus-project")
LOG_DIR = BASE_DIR / "memory" / "logs" / "security"
HEARTBEAT_FILE = BASE_DIR / "memory" / "logs" / "system" / "heartbeat.md"
AUDIT_FILE = LOG_DIR / "security_audit.md"

os.makedirs(LOG_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] SECURITY: {status}\n")

# ====== Checks ======
def check_permissions():
    issues = []
    for root, dirs, files in os.walk(BASE_DIR):
        for name in files:
            path = Path(root) / name
            try:
                mode = path.stat().st_mode
                if mode & 0o002:  # world-writable
                    issues.append(f"World-writable file: {path}")
            except:
                continue
    return issues

def check_packages():
    issues = []
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )
        if result.stdout:
            for line in result.stdout.splitlines()[2:]:
                parts = line.split()
                if len(parts) >= 3:
                    pkg, ver, latest = parts[0], parts[1], parts[2]
                    issues.append(f"Outdated package: {pkg} {ver} -> {latest}")
    except Exception as e:
        issues.append(f"Package audit error: {e}")
    return issues

def check_credentials():
    issues = []
    secret_patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),   # AWS keys
        re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),  # Stripe keys
        re.compile(r"TWILIO_[A-Z_]+"),     # Twilio env vars
        re.compile(r"[0-9a-fA-F]{32,}"),   # generic long hex
    ]
    scan_dirs = [BASE_DIR / "tools", BASE_DIR / "memory" / "logs"]
    for d in scan_dirs:
        for root, dirs, files in os.walk(d):
            for name in files:
                path = Path(root) / name
                try:
                    text = path.read_text(errors="ignore")
                    for pat in secret_patterns:
                        if pat.search(text):
                            issues.append(f"Potential credential in {path}")
                            break
                except:
                    continue
    return issues

# ====== Main ======
def run_audit():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    issues = []

    issues.extend(check_permissions())
    issues.extend(check_packages())
    issues.extend(check_credentials())

    with open(AUDIT_FILE, "a") as f:
        f.write(f"# Security Audit {ts}\n")
        if issues:
            for i in issues:
                f.write(f"- {i}\n")
            heartbeat_log(f"{len(issues)} issues detected")
        else:
            f.write("- No issues detected\n")
            heartbeat_log("Clean")

if __name__ == "__main__":
    try:
        # Only run full audit on 1st of each month
        if datetime.datetime.now().day == 1:
            run_audit()
        else:
            heartbeat_log("INFO: Audit skipped (not 1st of month)")
    except Exception as e:
        heartbeat_log(f"ERROR: Security audit crashed — {e}")
