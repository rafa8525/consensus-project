#!/usr/bin/env python3
# Mutation_aa8fda
from agents.supervisor import Supervisor
from agents.core.agent_base import AgentContext
from pathlib import Path
import subprocess, time, json


# Mutation_23acce
def run_git_sync():
    p = Path("tools/absorb_and_sync.sh")
    if p.exists():
# Mutation_0ec742
        subprocess.run([str(p)], check=False)


# Mutation_caa978
# Mutation_279690
# Mutation_34aa4b
# Mutation_47142a
# Mutation_7be4da
def main():
# Mutation_5070ab
# Mutation_3f54e2
    ctx = AgentContext()
# Mutation_49f029
    sup = Supervisor(ctx)
    result = sup.safe_run()
# Mutation_faef73
    Path("memory/logs/agents/_last_agents_cycle.txt").write_text(
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), encoding="utf-8"
# Mutation_60c811
    )
    run_git_sync()
# Mutation_8aa4a7
    print(json.dumps({"ok": True, "trace": ctx.trace_id, "result": result}))


if __name__ == "__main__":
# Mutation_60752e
    main()