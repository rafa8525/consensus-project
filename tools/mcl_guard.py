#!/usr/bin/env python3
import os, datetime, subprocess
from pathlib import Path

BASE = Path("/home/rafa1215/consensus-project")
SYSTEM_LOG_DIR = BASE / "memory/logs/system"
SYSTEM_LOG_DIR.mkdir(parents=True, exist_ok=True)

HEARTBEAT_FILE = SYSTEM_LOG_DIR / "heartbeat.md"

# -------------------------------------------------------------------
# Monitored files and their recovery scripts
# -------------------------------------------------------------------
FILES_TO_CHECK = {
    # Daily system reports
    "Daily status report": {
        "path": BASE / "memory/logs/system/project_status_daily.md",
        "script": BASE / "memory/logs/system/daily_status_autofill.py",
        "hours": 24,
    },
    # VPN reports
    "VPN test report": {
        "path": BASE / "memory/logs/system/vpn_test_report.md",
        "script": BASE / "tools/vpn_runner.py",
        "hours": 24,
    },
    # Progress evaluator
    "Progress evaluation report": {
        "path": BASE / "memory/logs/progress/progress_evaluation_report.md",
        "script": BASE / "tools/progress_evaluator.py",
        "hours": 24,
    },
    # Fitness logs
    "Fitness daily summary": {
        "path": BASE / "memory/logs/fitness/fitness_daily_summary.md",
        "script": BASE / "tools/fitness_integration.py",
        "hours": 24,
    },
    # Finance logs (weekly)
    "Finance audit log": {
        "path": BASE / "memory/logs/finance/finance_audit.md",
        "script": BASE / "tools/finance_master.py",
        "hours": 24*7,
    },
    # Security audits (monthly)
    "Security audit log": {
        "path": BASE / "memory/logs/security/security_audit.md",
        "script": BASE / "tools/security_reliability.py",
        "hours": 24*30,
    },
    # Knowledge sharing (daily)
    "Knowledge sharing summary": {
        "path": BASE / "memory/logs/progress/knowledge_sharing_summary.md",
        "script": BASE / "tools/knowledge_sharing.py",
        "hours": 24,
    },
}

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
def log_heartbeat(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] GUARD: {status}\n")

def check_file(path: Path, hours: int) -> bool:
    """Return True if file exists and is fresh within hours."""
    if not path.exists():
        return False
    mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    return (datetime.datetime.now() - mtime).total_seconds() < hours * 3600

def restart_task(script: Path, reason: str):
    """Run the script to auto-heal a missing/stale task."""
    try:
        subprocess.run(["/usr/bin/python3", str(script)], check=False)
        log_heartbeat(f"Auto-healed task: {script.name} ({reason})")
    except Exception as e:
        log_heartbeat(f"ERROR auto-healing {script.name}: {e}")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def run_guard():
    failures = []
    for name, meta in FILES_TO_CHECK.items():
        path, script, hours = meta["path"], meta["script"], meta["hours"]
        if not check_file(path, hours):
            failures.append(name)
            if script.exists():
                restart_task(script, f"{name} missing/stale")
            else:
                log_heartbeat(f"WARNING: No script found for {name}")
    if not failures:
        log_heartbeat("All monitored tasks healthy")
    else:
        log_heartbeat(f"Failures detected: {', '.join(failures)}")

if __name__ == "__main__":
    try:
        run_guard()
    except Exception as e:
        log_heartbeat(f"ERROR: Guard crashed — {e}")
