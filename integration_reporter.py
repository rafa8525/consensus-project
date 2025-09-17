#!/usr/bin/env python3
# integration_reporter.py
# Purpose: Summarize system health across guards and services into one report.
# Safe for PythonAnywhere. No emojis, no console-closing behavior.

import os
import json
import datetime
from pathlib import Path

# ===== CONFIG =====
PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
REPORT_FILE = LOG_DIR / "integration_report.md"

VOICE_GUARD_LOG = LOG_DIR / "voice_guard.log"
GITHUB_SYNC_LOG = LOG_DIR / "github_sync_launcher.log"
ABSORB_STATUS = LOG_DIR / "absorb_status.json"
ABSORB_GUARD_LOG = LOG_DIR / "absorb_guard.md"

# ===== UTILS =====
def now_iso():
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def safe_tail(path: Path, n=20):
    if not path.exists():
        return [f"{path.name} not found"]
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-n:]
    except Exception as e:
        return [f"Error reading {path.name}: {e}"]

def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

# ===== SECTION COLLECTORS =====
def collect_voice_guard():
    lines = safe_tail(VOICE_GUARD_LOG, 5)
    return ["### Voice Guard"] + lines

def collect_github_sync():
    lines = safe_tail(GITHUB_SYNC_LOG, 5)
    return ["### GitHub Sync"] + lines

def collect_absorb_guard():
    status = load_json(ABSORB_STATUS)
    lines = safe_tail(ABSORB_GUARD_LOG, 5)
    out = ["### Absorb Guard"]
    if status:
        out.append("Absorb Status JSON:")
        out.append(json.dumps(status, indent=2))
    else:
        out.append("No absorb_status.json available.")
    out.append("Recent absorb_guard.md lines:")
    out.extend(lines)
    return out

# ===== MAIN =====
def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    sections = []

    sections.append(f"# Integration Report\nGenerated {now_iso()}\n")

    sections.extend(collect_voice_guard())
    sections.append("")  # spacer
    sections.extend(collect_github_sync())
    sections.append("")
    sections.extend(collect_absorb_guard())

    REPORT_FILE.write_text("\n".join(sections), encoding="utf-8")
    print(f"[{now_iso()}] Integration report written to {REPORT_FILE}")

if __name__ == "__main__":
    main()
