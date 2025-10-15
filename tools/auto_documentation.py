#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Consensus System – Auto-Documentation & Self-Audit Module
Author: Rafael / AI Consensus System
Purpose: Automatically document agent improvements, file diffs, and commits.
"""

import os
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path.home() / "consensus-project"
LOG_DIR = BASE_DIR / "memory/logs/system/auto_docs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = LOG_DIR / f"auto_doc_{datetime.now(timezone.utc).date()}.md"

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def run_cmd(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=BASE_DIR, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.strip()}"

def gather_git_status():
    status = run_cmd(["git", "status", "--short"])
    log = run_cmd(["git", "log", "-1", "--pretty=format:%h %s (%cr)"])
    diff = run_cmd(["git", "diff", "--stat"])
    return {
        "status": status or "No changes.",
        "last_commit": log or "No commits yet.",
        "diff_summary": diff or "No diffs found."
    }

def list_recent_files():
    updated = []
    for root, _, files in os.walk(BASE_DIR / "tools"):
        for f in files:
            full = os.path.join(root, f)
            if f.endswith(".py") and (datetime.now().timestamp() - os.path.getmtime(full)) < 86400:
                updated.append(full.replace(str(BASE_DIR) + "/", ""))
    return updated or ["No modified Python files in the last 24h."]

def build_report():
    data = gather_git_status()
    files = list_recent_files()

    report = [
        f"# AI Consensus System – Auto-Documentation Report ({timestamp()})",
        "## Summary",
        "- Captures recent changes, agent updates, and commit information.",
        "",
        "## Git Status",
        "```",
        data["status"],
        "```",
        "",
        "### Last Commit",
        data["last_commit"],
        "",
        "### Diff Summary",
        "```",
        data["diff_summary"],
        "```",
        "",
        "## Recently Modified Python Files",
        "```",
        "\n".join(files),
        "```",
        "",
        "## Notes",
        "- This file was generated automatically by auto_documentation.py",
        "- For full history, see `memory/logs/system/auto_docs/`",
    ]

    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(f"✅ Auto-Documentation written to {REPORT_PATH}")

def archive_and_commit():
    msg = f"Auto-Doc: Weekly changelog update {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    run_cmd(["git", "add", str(REPORT_PATH)])
    run_cmd(["git", "commit", "-m", msg])
    run_cmd(["git", "push", "origin", "v1.1-dev"])

def main():
    print("=== Auto-Documentation Cycle Start ===")
    build_report()
    archive_and_commit()
    print("=== Auto-Documentation Cycle Complete ===")

if __name__ == "__main__":
    main()
