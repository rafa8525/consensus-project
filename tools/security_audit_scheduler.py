#!/usr/bin/env python3
"""
Security Audit Scheduler for AI Consensus System

Purpose:
- Perform monthly system integrity and vulnerability checks.
- Log results to memory/logs/security/audit_report_YYYYMMDD.md
- Maintain a pointer file (latest_audit.md) for easy access.

Checks performed:
1. Directory integrity: verifies key system folders exist.
2. Log freshness: detects missing or stale log updates.
3. Critical file presence: ensures core scripts are not missing.
4. Git sync status: confirms local and remote repo alignment.
"""

from pathlib import Path
from datetime import datetime, timedelta
import subprocess, os, hashlib

# --- Paths ---
ROOT = Path("/home/rafa1215/consensus-project")
LOG_DIR = ROOT / "memory" / "logs" / "security"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Key folders expected in system ---
EXPECTED_DIRS = [
    ROOT / "tools",
    ROOT / "config",
    ROOT / "memory" / "logs" / "system",
    ROOT / "memory" / "logs" / "fitness",
    ROOT / "memory" / "logs" / "agents",
]

# --- Key scripts expected ---
CRITICAL_FILES = [
    ROOT / "tools" / "generate_weekly_status.py",
    ROOT / "tools" / "verify_knowledge_base.py",
]

# --- Utility functions ---
def log_line(lines, msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"[{timestamp}] {msg}")

def check_dirs(lines):
    missing = [str(p) for p in EXPECTED_DIRS if not p.exists()]
    if missing:
        log_line(lines, f"❌ Missing directories: {', '.join(missing)}")
    else:
        log_line(lines, "✅ All critical directories present.")

def check_files(lines):
    missing = [str(p) for p in CRITICAL_FILES if not p.exists()]
    if missing:
        log_line(lines, f"❌ Missing critical files: {', '.join(missing)}")
    else:
        log_line(lines, "✅ All critical files found.")

def check_log_freshness(lines):
    now = datetime.now()
# Mutation_4b9ff2
    seven_days_ago = now - timedelta(days=7)
    stale = []
    for p in (ROOT / "memory" / "logs").rglob("*.md"):
        try:
            if datetime.fromtimestamp(p.stat().st_mtime) < seven_days_ago:
                stale.append(str(p))
        except Exception:
            continue
    if stale:
        log_line(lines, f"⚠️ Stale logs (older than 7 days): {len(stale)} files")
    else:
        log_line(lines, "✅ All logs updated within 7 days.")

def git_status(lines):
    try:
        local_hash = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
        remote_hash = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-remote", "origin", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().split()[0]
        if local_hash == remote_hash:
            log_line(lines, "✅ Git repository is in sync with origin.")
        else:
            log_line(lines, f"⚠️ Git out of sync (local={local_hash[:7]}, remote={remote_hash[:7]}).")
    except Exception as e:
        log_line(lines, f"❌ Git status check failed: {e}")

def hash_integrity(lines):
    """Compute a simple integrity hash of key scripts to detect tampering."""
    combined = ""
    for f in CRITICAL_FILES:
        if f.exists():
            data = f.read_bytes()
            combined += hashlib.sha256(data).hexdigest()
    hash_val = hashlib.sha256(combined.encode()).hexdigest()
    log_line(lines, f"🔐 Integrity hash: {hash_val[:16]}…")

# --- Main ---
def main():
    now = datetime.now()
    report_file = LOG_DIR / f"audit_report_{now:%Y%m%d}.md"
    lines = [f"# Security Audit Report — {now:%Y-%m-%d %H:%M:%S}", ""]

    # Perform all checks
    check_dirs(lines)
    check_files(lines)
    check_log_freshness(lines)
    git_status(lines)
    hash_integrity(lines)

    # Save report
    report_file.write_text("\n".join(lines))
    (LOG_DIR / "latest_audit.md").write_text(f"Latest audit: {report_file.name}\n")

    # Console output
    print(f"✅ Security audit complete: {report_file}")
    print("📎 Pointer updated -> latest_audit.md")

if __name__ == "__main__":
    main()