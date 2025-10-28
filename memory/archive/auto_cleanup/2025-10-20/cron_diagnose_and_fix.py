#!/usr/bin/env python3
"""
cron_diagnose_and_fix.py
Purpose:
    Diagnose why PythonAnywhere scheduled tasks (cron jobs) stop working,
    automatically collect environment differences, test permissions, and
    restore a clean, working configuration for daily_summary_generator.py.

Author: AI Consensus System
Date: 2025-10-07
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# --- Directories ---
HOME = Path.home()
ROOT = HOME / "consensus-project"
TOOLS = ROOT / "tools"
MEMORY = ROOT / "memory"
LOG_DIR = MEMORY / "logs" / "system"
SUMMARY_SCRIPT = TOOLS / "daily_summary_generator.py"
DIAG_LOG = LOG_DIR / f"cron_diag_{datetime.date.today()}.log"
DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    DIAG_LOG.open("a").write(line + "\n")

def capture_env(label, command):
    """Capture environment variables or command output"""
    log(f"--- Capturing {label} ---")
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        (LOG_DIR / f"{label.replace(' ', '_')}.txt").write_text(output)
        log(f"{label} captured successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Error capturing {label}: {e}")

def test_permissions():
    """Test write permissions to critical directories"""
    log("--- Testing directory write permissions ---")
    paths = [
        ROOT,
        TOOLS,
        MEMORY,
        MEMORY / "logs",
        LOG_DIR,
        MEMORY / "logs" / "system" / "agent_summaries"
    ]
    for p in paths:
        try:
            test_file = p / f"perm_test_{datetime.datetime.now().timestamp()}.tmp"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("test")
            test_file.unlink()
            log(f"✅ Write access OK: {p}")
        except Exception as e:
            log(f"❌ Write access FAILED: {p} ({e})")

def simulate_cron_run():
    """Simulate a cron run to reproduce errors"""
    log("--- Simulating cron-like execution ---")
    try:
        result = subprocess.run(
            [sys.executable, str(SUMMARY_SCRIPT)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90
        )
        log(f"Exit code: {result.returncode}")
        if result.stdout:
            (LOG_DIR / "cron_stdout.txt").write_text(result.stdout)
        if result.stderr:
            (LOG_DIR / "cron_stderr.txt").write_text(result.stderr)
        if result.returncode == 0:
            log("✅ Summary script executed successfully.")
        else:
            log("⚠️ Summary script returned a non-zero exit code. Check cron_stderr.txt.")
    except Exception as e:
        log(f"❌ Cron simulation failed: {e}")

def compare_envs():
    """Compare interactive vs cron environments"""
    log("--- Comparing environment snapshots ---")
    try:
        interactive = dict(os.environ)
        cron_env = (LOG_DIR / "cron_environment.txt").read_text().splitlines() if (LOG_DIR / "cron_environment.txt").exists() else []
        diffs = [line for line in cron_env if not any(line.startswith(k + "=") for k in interactive)]
        (LOG_DIR / "env_differences.txt").write_text("\n".join(diffs))
        log(f"Environment differences written to env_differences.txt")
    except Exception as e:
        log(f"❌ Failed to compare environments: {e}")

def restore_config():
    """If cron job missing or broken, recreate it"""
    log("--- Verifying crontab configuration ---")
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if "daily_summary_generator.py" not in result.stdout:
            new_entry = f"0 9 * * * /usr/bin/python3 {SUMMARY_SCRIPT} >> {LOG_DIR}/cron_output.log 2>&1\n"
            cron_content = result.stdout + "\n# Auto-restored by AI Consensus System\n" + new_entry
            subprocess.run(["bash", "-c", f'echo "{cron_content}" | crontab -'], check=True)
            log("✅ Restored missing crontab entry for daily_summary_generator.py.")
        else:
            log("✅ Cron entry for daily_summary_generator.py already exists.")
    except Exception as e:
        log(f"❌ Failed to check or restore crontab: {e}")

def main():
    log("=== Cron Diagnosis Script Started ===")
    capture_env("current_environment", "env")
    test_permissions()
    simulate_cron_run()
    compare_envs()
    restore_config()
    log("=== Cron Diagnosis Completed ===")

if __name__ == "__main__":
    main()
