#!/usr/bin/env python3
import os
import datetime
import subprocess

BASE_DIR = "/home/rafa1215/consensus-project/memory"
SECURITY_DIR = os.path.join(BASE_DIR, "logs/security")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(SECURITY_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] SECURITY: {status}\n")
    print(f"[HEARTBEAT] {status}")

def run_command(cmd):
    try:
        result = subprocess.getoutput(cmd)
        return result.strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_security_audit():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(SECURITY_DIR, f"security_audit_{ts}.md")

    checks = {}
    checks["Open Ports"] = run_command("ss -tuln | head -20")
    checks["Running Processes"] = run_command("ps -eo pid,comm --sort=-%mem | head -10")
    checks["Disk Usage"] = run_command("df -h | head -10")
    checks["Recent Auth Failures"] = run_command("grep 'Failed password' /var/log/auth.log | tail -10 || echo 'No access to auth.log'")
    checks["Firewall Status"] = run_command("ufw status || echo 'ufw not installed'")
    checks["System Updates"] = run_command("apt list --upgradable 2>/dev/null | head -10")

    with open(report_file, "w") as f:
        f.write(f"# Security Audit Report — {ts}\n\n")
        for section, result in checks.items():
            f.write(f"## {section}\n```\n{result}\n```\n\n")

    heartbeat_log("SUCCESS: Security audit completed")
    return report_file

if __name__ == "__main__":
    # Only run on the 1st of each month
    if datetime.datetime.now().day != 1:
        heartbeat_log("INFO: Audit skipped (not 1st of month)")
        exit(0)

    try:
        report = run_security_audit()
        print(f"Security audit saved: {report}")
    except Exception as e:
        heartbeat_log(f"ERROR: Security audit failed — {e}")
