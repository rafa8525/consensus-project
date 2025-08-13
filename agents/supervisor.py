from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import json, time

from agents.core.agent_base import Agent, AgentContext
from agents.core.metrics import record
from agents.core import store

class Supervisor(Agent):
    name = "supervisor"

    def run(self) -> Dict[str, Any]:
        cfg = json.loads(Path("memory/config/agents.json").read_text(encoding="utf-8"))
        plan = []

        # Example planning (expandable):
        if cfg.get("tasks", {}).get("log_audit", True):
            plan.append({"task": "log_audit"})

        if cfg.get("tasks", {}).get("self_improve", True):
            plan.append({"task": "self_improve"})

        # orchestrate children
        results = {}
        if any(t["task"] == "log_audit" for t in plan):
            from agents.researcher import Researcher
            results["log_audit"] = Researcher(self.ctx).safe_run()

        if any(t["task"] == "self_improve" for t in plan):
            from agents.self_improver import SelfImprover
            results["self_improve"] = SelfImprover(self.ctx).safe_run()

        # evaluator at the end
        from agents.evaluator import Evaluator
        results["evaluation"] = Evaluator(self.ctx).safe_run()

        # persist small shared state
        st = store.load()
        st["last_supervisor_ts"] = time.time()
        store.save(st)

        record("supervisor_cycle", status="ok")
        return results
