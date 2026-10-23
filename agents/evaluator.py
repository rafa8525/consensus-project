from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import time
from agents.core.agent_base import Agent


class Evaluator(Agent):
    name = "evaluator"

    def run(self) -> Dict[str, Any]:
        root = Path("memory/logs/agents")
        latest_reports = sorted(root.glob("knowledge_shared_*.md"))[-3:]
        latest_improve = sorted(root.glob("self_improvement_*.md"))[-3:]
        # Use prior-cycle lessons from real ACS-02..05 failures. Read-only:
        # recommendations require review and never execute repair code.
        from tools.shared_agent_lessons import consume
        lessons = consume(Path.cwd())
        summary = [
            "# Evaluation summary",
            f"- reports: {len(latest_reports)}",
            f"- improvements: {len(latest_improve)}",
            f"- verified prior-cycle lessons: {len(lessons)}",
        ]
        for lesson in lessons:
            summary.append(f"- {lesson['producer']} / {lesson['incident']}: {lesson['recommendation']}")
        out = self.write_artifact(
            f"lessons_learned_{time.strftime('%Y-%m-%d', time.gmtime())}.md",
            "\n".join(summary) + "\n",
        )
        return {"summary": str(out), "lessons_used": len(lessons)}
