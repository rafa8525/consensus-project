#!/usr/bin/env python3
"""
System Bootstrap — AI Consensus System
--------------------------------------

Purpose:
Launch all active modules in correct sequence:
1. Knowledge Base verification
2. Weekly status generator
3. Security audit scheduler
4. VPN test suite
5. Progress evaluator
6. Fitness integration
7. Fitness↔VPN Smart Link

Each run logs a heartbeat report to memory/logs/system/bootstrap_YYYYMMDD_HHMM.md
"""

from pathlib import Path
from datetime import datetime
import subprocess, sys

ROOT = Path("/home/rafa1215/consensus-project")
TOOLS = ROOT / "tools"
LOG_DIR = ROOT / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)

MODULES = [
    "verify_knowledge_base.py",
    "generate_weekly_status.py",
    "security_audit_scheduler.py",
    "vpn_test_suite.py",
    "progress_evaluator.py",
    "fitness_integration.py",
    "fitness_vpn_smartlink.py",
]

def run_module(name: str, lines: list[str]):
    """Execute a single module and log its output."""
    ts = datetime.now().strftime("%H:%M:%S")
    path = TOOLS / name
    if not path.exists():
        lines.append(f"[{ts}] ⚠️ Missing module: {name}")
        return
    lines.append(f"[{ts}] ▶ Running {name} …")
    try:
        out = subprocess.check_output(
            [sys.executable, str(path)],
            stderr=subprocess.STDOUT,
            timeout=60
        ).decode().strip()
        lines.append(f"[{ts}] ✅ Success — {name}")
        if out:
            for line in out.splitlines():
                lines.append(f"    {line}")
    except subprocess.CalledProcessError as e:
        lines.append(f"[{ts}] ❌ Error in {name}: {e.output.decode(errors='ignore')}")
    except subprocess.TimeoutExpired:
        lines.append(f"[{ts}] ⏰ Timeout — {name}")

def main():
    now = datetime.now()
    report = LOG_DIR / f"bootstrap_{now:%Y%m%d_%H%M}.md"
    lines = [
        f"# System Bootstrap — {now:%Y-%m-%d %H:%M:%S}",
        f"Working directory: {ROOT}",
        ""
    ]

    for mod in MODULES:
        run_module(mod, lines)

    lines.append("")
    lines.append("All modules executed. System up to date.")
    report.write_text("\n".join(lines))
    (LOG_DIR / "latest_bootstrap.md").write_text(f"Latest bootstrap run: {report.name}\n")

    print(f"✅ System bootstrap complete → {report}")
    print("📎 Pointer updated → latest_bootstrap.md")

if __name__ == "__main__":
    main()
