#!/usr/bin/env python3
"""
morning_master.py — Morning orchestrator (lean)

What it does (idempotent):
  1) Logs a heartbeat to ~/memory/logs/system/morning_master.log
  2) Publishes a daily status report via tools/publish_status_report.py
  3) Optional hooks (toggle with env):
       RUN_AGENT_INDEX   (default: true)  -> tools/agent_log_indexer.py
       RUN_MOVIES_MON    (default: false) -> tools/movies_monitor.py
       RUN_GMAIL_DIGEST  (default: false) -> tools/gmail_unread_digest.py
  4) Writes a short summary to ~/memory/logs/system/morning_master_summary.md

Exit: 0 on success. Nonzero if critical failures (very rare).
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ---- Paths ----
HOME   = Path.home()
ROOT   = HOME / "consensus-project"
TOOLS  = ROOT / "tools"
LOGDIR = HOME / "memory" / "logs" / "system"
RPTDIR = HOME / "memory" / "logs" / "reports"

LOGDIR.mkdir(parents=True, exist_ok=True)
RPTDIR.mkdir(parents=True, exist_ok=True)

RUNLOG   = LOGDIR / "morning_master.log"
SUMMARY  = LOGDIR / "morning_master_summary.md"

UTC_NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ---- Env toggles (keep it lean by default) ----
RUN_AGENT_INDEX  = os.environ.get("RUN_AGENT_INDEX",  "true").lower() == "true"
RUN_MOVIES_MON   = os.environ.get("RUN_MOVIES_MON",   "false").lower() == "true"
RUN_GMAIL_DIGEST = os.environ.get("RUN_GMAIL_DIGEST", "false").lower() == "true"

def log_line(msg: str):
    line = f"[{UTC_NOW()}] {msg}"
    print(line)
    with RUNLOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_tool(name: str, timeout=600):
    """Run a tool in ~/consensus-project/tools, capture rc/out/err."""
    p = TOOLS / name
    if not p.exists():
        log_line(f"MISS: {name} not found")
        return {"tool": name, "rc": 127, "err": "not found", "out": ""}

    try:
        res = subprocess.run(
            ["python3", str(p)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        rc  = res.returncode
        out = (res.stdout or "")[-1000:]
        err = (res.stderr or "")[-800:]
        log_line(f"{name} rc={rc}")
        return {"tool": name, "rc": rc, "out": out, "err": err}
    except Exception as e:
        log_line(f"{name} EXC: {e}")
        return {"tool": name, "rc": -1, "out": "", "err": f"EXC:{e}"}

def write_summary(results):
    ok = all(r.get("rc", 1) == 0 for r in results if r) if results else True
    lines = [
        "# Morning Master Summary",
        f"UTC: {UTC_NOW()}",
        f"Status: {'OK' if ok else 'ISSUES'}",
        "",
        "## Steps"
    ]
    for r in results:
        if not r: 
            continue
        lines.append(f"- {r['tool']}: rc={r['rc']}")
        if r["rc"] != 0 and r.get("err"):
            lines.append(f"  - err: {r['err'][:400]}")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ok

def main():
    log_line("=== morning_master start ===")
    results = []

    # 1) Status report (always)
    results.append(run_tool("publish_status_report.py", timeout=300))

    # 2) Optional light hooks (lean by default)
    if RUN_AGENT_INDEX:
        results.append(run_tool("agent_log_indexer.py", timeout=240))
    if RUN_MOVIES_MON:
        results.append(run_tool("movies_monitor.py", timeout=300))
    if RUN_GMAIL_DIGEST:
        results.append(run_tool("gmail_unread_digest.py", timeout=300))

    ok = write_summary(results)
    log_line(f"summary written -> {SUMMARY}")
    log_line(f"=== morning_master end ({'OK' if ok else 'ISSUES'}) ===")
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
