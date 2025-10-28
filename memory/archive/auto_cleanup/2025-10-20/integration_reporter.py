#!/usr/bin/env python3
# integration_reporter.py
# Purpose: Unified health reporter for core services with daily roll-ups

import os
import datetime
from pathlib import Path

PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
REPORT_FILE = LOG_DIR / "integration_report.md"
DATESTAMP = datetime.date.today().isoformat()
DAILY_FILE = LOG_DIR / f"integration_report_{DATESTAMP}.md"

# Known log sources
VOICE_GUARD_LOG = LOG_DIR / "voice_guard.md"
GITHUB_SYNC_LOG = LOG_DIR / "github_sync_launcher.log"
ABSORB_MD = LOG_DIR / "absorb_guard.md"
ABSORB_STATUS_JSON = LOG_DIR / "absorb_status.json"

def now_iso():
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def tail_lines(path: Path, n: int = 20):
    """Read the last N lines of a file, or return a message if missing."""
    if not path.exists():
        return [f"{path.name} not found"]
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        return lines[-n:] if lines else ["(empty)"]

def build_report():
    lines = []
    lines.append("# Integration Report")
    lines.append(f"Generated {now_iso()}")

    # --- Voice Guard ---
    lines.append("### Voice Guard")
    lines.extend([f"    {l.strip()}" for l in tail_lines(VOICE_GUARD_LOG, 10)])

    # --- GitHub Sync ---
    lines.append("### GitHub Sync")
    lines.extend([f"    {l.strip()}" for l in tail_lines(GITHUB_SYNC_LOG, 15)])

    # --- Absorb Guard ---
    lines.append("### Absorb Guard")
    if ABSORB_STATUS_JSON.exists():
        try:
            data = ABSORB_STATUS_JSON.read_text(encoding="utf-8")
            lines.append("Absorb Status JSON:")
            lines.append("```json")
            lines.append(data.strip())
            lines.append("```")
        except Exception as e:
            lines.append(f"    Failed to read absorb_status.json: {e}")
    lines.append("Recent absorb_guard.md lines:")
    lines.extend([f"    {l.strip()}" for l in tail_lines(ABSORB_MD, 10)])

    return "\n".join(lines) + "\n"

def write_reports():
    report = build_report()
    os.makedirs(LOG_DIR, exist_ok=True)

    # Rolling report
    with REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write(report)

    # Daily roll-up (append so history accumulates)
    with DAILY_FILE.open("a", encoding="utf-8") as f:
        f.write(report)
        f.write("\n---\n\n")

    print(f"[{now_iso()}] Integration report written to {REPORT_FILE} and {DAILY_FILE}")

if __name__ == "__main__":
    write_reports()
