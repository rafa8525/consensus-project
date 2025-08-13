#!/usr/bin/env python3
from __future__ import annotations
from agents.supervisor import Supervisor
from agents.core.agent_base import AgentContext
from pathlib import Path
import subprocess, os, sys, time, json

def run_git_sync():
    # Reuse existing sync script if present
    p = Path("tools/absorb_and_sync.sh")
    if p.exists():
        subprocess.run([str(p)], check=False)

def main():
    ctx = AgentContext()
    sup = Supervisor(ctx)
    result = sup.safe_run()

    # Append a small stamp so Git has something to commit when only logs changed
    Path("memory/logs/agents/_last_agents_cycle.txt").write_text(
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), encoding="utf-8"
    )

    run_git_sync()
    print(json.dumps({"ok": True, "trace": ctx.trace_id, "result": result}))

if __name__ == "__main__":
    main()
