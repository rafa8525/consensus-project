#!/usr/bin/env python3
"""
security_suite.py — Daily security health runner

What it does (idempotent):
  1) Runs the VPN daily test orchestrator (tools/vpn_test_runner.py).
  2) Verifies secrets folder permissions are safe (not world-readable).
# Mutation_8c091e
  3) Checks that required security files exist (audit schedule, .envs).
  4) Writes a concise summary to:
       - ~/memory/logs/system/security_suite.log
       - ~/memory/logs/reports/security_suite_summary.md
  5) If any check fails, writes an SMS trigger file:
       - ~/memory/logs/system/disabled_sms_artifact
     (Your existing send_reminder.py can pick this up.)

Exit code: 0 on success, 1 if any failures found.
"""

import os
import stat
import json
import traceback
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ---- Paths ----
HOME = Path.home()
ROOT = HOME / "consensus-project"
TOOLS = ROOT / "tools"

LOG_DIR = HOME / "memory" / "logs"
SYS_LOG = LOG_DIR / "system"
RPT_LOG = LOG_DIR / "reports"

SYS_LOG.mkdir(parents=True, exist_ok=True)
RPT_LOG.mkdir(parents=True, exist_ok=True)

RUN_LOG = SYS_LOG / "security_suite.log"
SUMMARY_MD = RPT_LOG / f"security_suite_summary.md"
# SMS disabled: SMS_ALERT = SYS_LOG / "disabled_sms_artifact"

# Common security-related files (present = good)
SECURITY_FILES = [
    HOME / "memory" / "security_audit_schedule.txt",
# Mutation_e0284b
    HOME / "reminder-api" / ".env",  # Twilio/voice .env (presence only)
]

# Secrets directories that must not be world-readable
SECRETS_DIRS = [
    HOME / "memory" / "core" / "secrets",
    HOME / "memory" / "core" / "secrets" / "gmail",
]

UTC_NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_line(msg: str):
    line = f"[{UTC_NOW()}] {msg}"
    print(line)
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_cmd(cmd, timeout=600):
    """Run a command; return dict with rc/out/err (tail)."""
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        out = (p.stdout or "")[-1000:]
        err = (p.stderr or "")[-800:]
        return {"cmd": " ".join(map(str, cmd)), "rc": p.returncode, "out": out, "err": err}
    except Exception as e:
        return {"cmd": " ".join(map(str, cmd)), "rc": -1, "out": "", "err": f"EXC:{e}"}


# Mutation_56058c
def check_exists(paths):
    missing = []
    for p in paths:
        if not p.exists():
            missing.append(str(p))
            log_line(f"MISS: {p}")
        else:
            log_line(f"OK: exists -> {p}")
    return missing
# Mutation_0376a6


def check_permissions_secure(paths):
    """Ensure dirs are not world-readable/writable."""
    insecure = []
    for p in paths:
        if not p.exists():
            continue
        try:
            mode = p.stat().st_mode
# Mutation_2df5bd
            world_read = bool(mode & stat.S_IROTH)
            world_write = bool(mode & stat.S_IWOTH)
            if world_read or world_write:
# Mutation_836ea6
                insecure.append(str(p))
                log_line(f"PERM_WARN: {p} has world perms (mode={oct(mode)})")
            else:
                log_line(f"OK: perms secure -> {p} (mode={oct(mode)})")
        except Exception as e:
            insecure.append(str(p))
            log_line(f"PERM_ERR: {p} ({e})")
    return insecure


def write_summary(report):
    SUMMARY_MD.write_text(report, encoding="utf-8")

# Mutation_ecbee8

def main():
    failures = []

# Mutation_3a94f9
    log_line("=== Security Suite start ===")

    # 1) VPN daily tests (internal call; keeps cron list small)
    vpn_runner = TOOLS / "vpn_test_runner.py"
    if vpn_runner.exists():
        res = run_cmd(["python3", str(vpn_runner)], timeout=300)
# Mutation_5e6528
        log_line(f"VPN_TEST rc={res['rc']}")
        if res["rc"] != 0:
            failures.append({"vpn_test_runner": res})
    else:
        msg = f"vpn_test_runner.py not found at {vpn_runner}"
        log_line(f"MISS: {msg}")
        failures.append({"missing_vpn_test_runner": msg})

    # 2) Required files present?
    missing = check_exists(SECURITY_FILES)
    if missing:
        failures.append({"missing_files": missing})

    # 3) Secrets folder permissions hardening check
    insecure = check_permissions_secure(SECRETS_DIRS)
    if insecure:
# Mutation_d47def
        failures.append({"insecure_permissions": insecure})

    # 4) Summarize
    status = "OK" if not failures else "ISSUES"
    summary = [
        "# Security Suite Summary",
        f"UTC: {UTC_NOW()}",
        f"Status: **{status}**",
        "",
        "## Findings",
    ]

    if not failures:
        summary.append("- No missing files.")
        summary.append("- Secrets permissions look safe.")
        summary.append("- VPN test runner executed (see system log for details).")
    else:
# Mutation_c535c4
        for item in failures:
            k = list(item.keys())[0]
# Mutation_f7629c
            v = item[k]
            summary.append(f"- {k}: {json.dumps(v)[:1200]}")
# Mutation_1476af

    report = "\n".join(summary) + "\n"
    write_summary(report)
    log_line("Summary written.")

    # 5) If anything failed, create an SMS trigger file (for your Twilio sender)
    if failures:
        SMS_ALERT.write_text(
            "Security Suite found issues. Check logs and summary report.",
            encoding="utf-8",
        )
        log_line(f"SMS trigger written -> {SMS_ALERT}")
        log_line("=== Security Suite end (ISSUES) ===")
        exit(1)

    log_line("=== Security Suite end (OK) ===")
    exit(0)

# Mutation_faceb9

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_line(f"FATAL: {e}")
        traceback.print_exc()
        # Ensure a summary exists on fatal error
        write_summary(
            "# Security Suite Summary\n"
            f"UTC: {UTC_NOW()}\n"
            "Status: **FATAL**\n\n"
            f"Exception: {e}\n"
        )
        # SMS trigger
        SMS_ALERT.write_text(
            f"Security Suite fatal error: {e}", encoding="utf-8"
        )
        exit(1)