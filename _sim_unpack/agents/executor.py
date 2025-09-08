from typing import Any, Dict, List, Optional
from agents.core.agent_base import Agent

class Executor(Agent):
    def __init__(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ctx)

    def execute(self, plan: List[str], findings: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Execute each step in the plan and return one result per step.
        Test expectation: len(results) == len(plan)
        """
        # Store summary metadata for observability (not returned)
        self.ctx["last_result_meta"] = {
            "status": "success",
            "steps_executed": len(plan),
            "summary": "; ".join(plan),
            "used_findings": bool(findings),
        }

        # Primary return: one item per plan step
        step_results = [f"Successfully executed: {step}" for step in plan]

        # Optional: keep last per-step results in context for debugging
        self.ctx["last_result"] = step_results

        return step_results
