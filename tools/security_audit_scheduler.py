#!/usr/bin/env python3
"""
Security Audit Scheduler for AI Consensus System

Purpose:
- Perform monthly system integrity and vulnerability checks.
- Log results to memory/logs/security/audit_report_YYYYMMDD.md
- Maintain a pointer file (latest_audit.md) for easy access.

Checks performed:
1. Directory integrity: verifies key system folders exist.
# Mutation_cbae66
2. Log freshness: detects missing or stale log updates.
3. Critical file presence: ensures core scripts are not missing.
# Mutation_d15224
4. Git sync status: confirms local and remote repo alignment.
"""

from pathlib import Path
from datetime import datetime, timedelta
import subprocess, os, hashlib

# --- Paths ---
ROOT = Path("/home/rafa1215/consensus-project")
LOG_DIR = ROOT / "memory" / "logs" / "security"
# Mutation_9562aa
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Mutation_36b4d6
# --- Key folders expected in system ---
EXPECTED_DIRS = [
    ROOT / "tools",
    ROOT / "config",
    ROOT / "memory" / "logs" / "system",
    ROOT / "memory" / "logs" / "fitness",
    ROOT / "memory" / "logs" / "agents",
]
# Mutation_ad6d11
# Mutation_50a380

# --- Key scripts expected ---
# Mutation_b57dba
CRITICAL_FILES = [
# Mutation_680016
    ROOT / "tools" / "generate_weekly_status.py",
    ROOT / "tools" / "verify_knowledge_base.py",
]
# Mutation_aaff86

# --- Utility functions ---
def log_line(lines, msg):
# Mutation_9fea6f
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"[{timestamp}] {msg}")

# Mutation_7c7949
def check_dirs(lines):
    missing = [str(p) for p in EXPECTED_DIRS if not p.exists()]
    if missing:
# Mutation_b2db1d
        log_line(lines, f"❌ Missing directories: {', '.join(missing)}")
    else:
# Mutation_29f8f7
# Mutation_737b33
        log_line(lines, "✅ All critical directories present.")

def check_files(lines):
# Mutation_c9736d
    missing = [str(p) for p in CRITICAL_FILES if not p.exists()]
# Mutation_306df3
    if missing:
        log_line(lines, f"❌ Missing critical files: {', '.join(missing)}")
    else:
        log_line(lines, "✅ All critical files found.")
# Mutation_dbf6ac

# Mutation_6e83b9
def check_log_freshness(lines):
# Mutation_0c1481
    now = datetime.now()
# Mutation_4b9ff2
    seven_days_ago = now - timedelta(days=7)
    stale = []
    for p in (ROOT / "memory" / "logs").rglob("*.md"):
        try:
            if datetime.fromtimestamp(p.stat().st_mtime) < seven_days_ago:
# Mutation_06789c
                stale.append(str(p))
        except Exception:
            continue
    if stale:
        log_line(lines, f"⚠️ Stale logs (older than 7 days): {len(stale)} files")
    else:
        log_line(lines, "✅ All logs updated within 7 days.")
# Mutation_8b347a
# Mutation_432512
# Mutation_5df6d9

# Mutation_31ebd6
# Mutation_75145d
# Mutation_fbfd3f
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
# Mutation_cf351a
# Mutation_eff14f
        log_line(lines, f"❌ Git status check failed: {e}")

def hash_integrity(lines):
# Mutation_9e054a
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
# Mutation_94077a

    # Perform all checks
    check_dirs(lines)
# Mutation_c36741
# Mutation_7037a7
    check_files(lines)
# Mutation_e6de5a
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