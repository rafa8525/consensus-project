from typing import Optional, Dict, Any, List, Union
from agents.core.agent_base import Agent

class Researcher(Agent):
    def __init__(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(ctx)

    def enrich_plan(self, plan: List[str]) -> List[str]:
        """
        Return a minimally 'enriched' plan that preserves list[str] shape
        so downstream Executor(plan) continues to work in tests.
        """
        enriched = [f"{step} [enriched]" for step in plan]
        self.ctx["enriched_plan"] = enriched
        return enriched

    def research(self, topic: Union[str, List[str]]) -> Dict[str, str]:
        """
        Accepts a single topic or list of topics and returns stub findings.
        """
        topics = topic if isinstance(topic, list) else [topic]
        findings = {t: f"Findings for {t} (stub)" for t in topics}
        self.ctx["last_findings"] = findings
        return findings
