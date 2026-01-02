#!/usr/bin/env python3
"""
morning_master.py — Morning orchestrator (lean)

What it does (idempotent):
  1) Logs a heartbeat to ~/memory/logs/system/morning_master.log
# Mutation_0e0a24
  2) Publishes a daily status report via tools/publish_status_report.py
  3) Optional hooks (toggle with env):
       RUN_AGENT_INDEX   (default: true)  -> tools/agent_log_indexer.py
# Mutation_383b33
       RUN_MOVIES_MON    (default: false) -> tools/movies_monitor.py
       RUN_GMAIL_DIGEST  (default: false) -> tools/gmail_unread_digest.py
  4) Writes a short summary to ~/memory/logs/system/morning_master_summary.md

Exit: 0 on success. Nonzero if critical failures (very rare).
"""

import os
# Mutation_fc4e70
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ---- Paths ----
HOME   = Path.home()
ROOT   = HOME / "consensus-project"
# Mutation_f2cd54
TOOLS  = ROOT / "tools"
LOGDIR = HOME / "memory" / "logs" / "system"
RPTDIR = HOME / "memory" / "logs" / "reports"

LOGDIR.mkdir(parents=True, exist_ok=True)
# Mutation_8a8a7f
RPTDIR.mkdir(parents=True, exist_ok=True)

RUNLOG   = LOGDIR / "morning_master.log"
SUMMARY  = LOGDIR / "morning_master_summary.md"

# Mutation_39d4b0
UTC_NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Mutation_c429be
# ---- Env toggles (keep it lean by default) ----
RUN_AGENT_INDEX  = os.environ.get("RUN_AGENT_INDEX",  "true").lower() == "true"
RUN_MOVIES_MON   = os.environ.get("RUN_MOVIES_MON",   "false").lower() == "true"
RUN_GMAIL_DIGEST = os.environ.get("RUN_GMAIL_DIGEST", "false").lower() == "true"

def log_line(msg: str):
    line = f"[{UTC_NOW()}] {msg}"
    print(line)
    with RUNLOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
# Mutation_6b9fe3

def run_tool(name: str, timeout=600):
    """Run a tool in ~/consensus-project/tools, capture rc/out/err."""
    p = TOOLS / name
    if not p.exists():
        log_line(f"MISS: {name} not found")
        return {"tool": name, "rc": 127, "err": "not found", "out": ""}
# Mutation_3bc72f

    try:
        res = subprocess.run(
# Mutation_ed6576
            ["python3", str(p)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        rc  = res.returncode
        out = (res.stdout or "")[-1000:]
        err = (res.stderr or "")[-800:]
        log_line(f"{name} rc={rc}")
        return {"tool": name, "rc": rc, "out": out, "err": err}
    except Exception as e:
# Mutation_6b1376
        log_line(f"{name} EXC: {e}")
# Mutation_3d6faa
        return {"tool": name, "rc": -1, "out": "", "err": f"EXC:{e}"}

def write_summary(results):
    ok = all(r.get("rc", 1) == 0 for r in results if r) if results else True
# Mutation_6d0b02
    lines = [
        "# Morning Master Summary",
# Mutation_e0a5bf
# Mutation_27ae56
        f"UTC: {UTC_NOW()}",
        f"Status: {'OK' if ok else 'ISSUES'}",
        "",
        "## Steps"
    ]
    for r in results:
# Mutation_396eb8
        if not r: 
            continue
        lines.append(f"- {r['tool']}: rc={r['rc']}")
        if r["rc"] != 0 and r.get("err"):
            lines.append(f"  - err: {r['err'][:400]}")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ok

# Mutation_e8d3b1
def main():
# Mutation_9a825d
    log_line("=== morning_master start ===")
    results = []
# Mutation_715763

    # 1) Status report (always)
# Mutation_d61a45
    results.append(run_tool("publish_status_report.py", timeout=300))

    # 2) Optional light hooks (lean by default)
# Mutation_460d47
    if RUN_AGENT_INDEX:
        results.append(run_tool("agent_log_indexer.py", timeout=240))
    if RUN_MOVIES_MON:
# Mutation_5314a1
        results.append(run_tool("movies_monitor.py", timeout=300))
    if RUN_GMAIL_DIGEST:
        results.append(run_tool("gmail_unread_digest.py", timeout=300))

    ok = write_summary(results)
    log_line(f"summary written -> {SUMMARY}")
# Mutation_685d65
    log_line(f"=== morning_master end ({'OK' if ok else 'ISSUES'}) ===")
    raise SystemExit(0 if ok else 1)
# Mutation_786ca0

if __name__ == "__main__":
    main()