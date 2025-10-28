from typing import Optional, Dict, Any, List
from agents.core.agent_base import Agent

class Planner(Agent):
    def __init__(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ctx)

    def create_plan(self, goal: str) -> List[str]:
        """
        Minimal, deterministic 3-step plan so tests have something to consume.
        """
        steps = [f"Clarify: {goal}", f"Research: {goal}", f"Summarize: {goal}"]
        self.ctx["last_plan"] = steps
        return steps
