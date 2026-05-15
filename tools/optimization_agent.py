#!/usr/bin/env python3
"""
optimization_agent.py

Safe optimization layer for Rafael's AI Consensus System.

Purpose:
- Learn from recent healthy or unhealthy runs
- Detect recurring patterns in decisions and executions
- Suggest safe, concrete improvements
- Write both human-readable and machine-readable optimization outputs

Version 1 principles:
- file-based only
- no destructive actions
- no automatic config mutation
- optimize by observation first
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


@dataclass
class OptimizationSuggestion:
    category: str
    priority: str   # high | medium | low
    title: str
    rationale: str
    proposed_action: str


class OptimizationAgent:
    def __init__(self, mem_root: Path, repo_root: Path, dry_run: bool = False) -> None:
        self.mem_root = mem_root
        self.repo_root = repo_root
        self.dry_run = dry_run

        self.decisions_dir = self.mem_root / "logs" / "decisions"
        self.status_dir = self.mem_root / "logs" / "status"
        self.system_exec_dir = self.mem_root / "logs" / "system" / "exec"
        self.optimization_dir = self.mem_root / "logs" / "optimization"

        self.report_path = self.optimization_dir / "optimization_report.md"
        self.audit_path = self.system_exec_dir / "optimization_agent_audit.log"

    def run(self) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)
        today = now_local.date().isoformat()

        self._ensure_dirs()

        latest_decision = self._load_latest_decision(today)
        recent_decisions = self._load_recent_decisions(limit=7)
        recent_execution_lines = self._read_recent_lines(
            self.system_exec_dir / "execution_agent_audit.log",
            limit=40,
        )

        overall_state = str(latest_decision.get("overall_state", "UNKNOWN")).upper()
        confidence = str(latest_decision.get("confidence", "UNKNOWN")).upper()

        suggestions = self._build_suggestions(
            latest_decision=latest_decision,
            recent_decisions=recent_decisions,
            recent_execution_lines=recent_execution_lines,
        )

        summary = self._build_summary(
            overall_state=overall_state,
            confidence=confidence,
            recent_decisions=recent_decisions,
            suggestions=suggestions,
        )

        output = {
            "generated_local": now_local.isoformat(),
            "generated_utc": now_utc.isoformat(),
            "overall_state_seen": overall_state,
            "confidence_seen": confidence,
            "summary": summary,
            "suggestions": [asdict(s) for s in suggestions],
        }

        if not self.dry_run:
            self._write_report(output)
            self._write_json(today, output)
            self._append_audit_log(output)

        return output

    def _ensure_dirs(self) -> None:
        self.optimization_dir.mkdir(parents=True, exist_ok=True)
        self.system_exec_dir.mkdir(parents=True, exist_ok=True)

    def _load_latest_decision(self, today: str) -> Dict[str, Any]:
        today_path = self.decisions_dir / f"{today}_decision.json"
        if today_path.exists():
            return self._read_json(today_path)

        candidates = sorted(self.decisions_dir.glob("*_decision.json"))
        if not candidates:
            return {}
        return self._read_json(candidates[-1])

    def _load_recent_decisions(self, limit: int = 7) -> List[Dict[str, Any]]:
        candidates = sorted(self.decisions_dir.glob("*_decision.json"))[-limit:]
        return [self._read_json(path) for path in candidates]

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _read_recent_lines(self, path: Path, limit: int = 40) -> List[str]:
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            return lines[-limit:]
        except Exception:
            return []

    def _build_suggestions(
        self,
        latest_decision: Dict[str, Any],
        recent_decisions: List[Dict[str, Any]],
        recent_execution_lines: List[str],
    ) -> List[OptimizationSuggestion]:
        suggestions: List[OptimizationSuggestion] = []

        overall_state = str(latest_decision.get("overall_state", "UNKNOWN")).upper()
        confidence = str(latest_decision.get("confidence", "UNKNOWN")).upper()
        evidence = latest_decision.get("evidence", []) if isinstance(latest_decision.get("evidence"), list) else []

        # 1. Stable healthy system -> optimize monitoring cadence or promote more proactive work
        if overall_state == "OK" and confidence == "HIGH":
            suggestions.append(
                OptimizationSuggestion(
                    category="stability",
                    priority="medium",
                    title="Promote from reactive maintenance to proactive optimization",
                    rationale="The system is currently healthy and stable, so the highest-value work is now preventive and performance-oriented rather than repair-oriented.",
                    proposed_action="Add a weekly scorecard and a morning executive brief so healthy runs still produce useful value.",
                )
            )

        # 2. Look for aging-but-OK evidence, such as prediction feed older than a few hours
        for item in evidence:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", ""))
            age_hours = item.get("age_hours")
            if name == "prediction_feed" and isinstance(age_hours, (int, float)) and age_hours >= 4:
                suggestions.append(
                    OptimizationSuggestion(
                        category="freshness",
                        priority="medium",
                        title="Tighten prediction feed freshness",
                        rationale=f"Prediction feed is healthy but already {age_hours:.1f} hours old, which suggests you may get more value by running it earlier or more consistently.",
                        proposed_action="Review the schedule for prediction feed generation and consider moving it earlier or adding a second lightweight refresh pass.",
                    )
                )
                break

        # 3. If recent execution logs show repeated healthy traces, shift effort toward optimization
        healthy_trace_count = sum("name=healthy_state_trace status=executed" in line for line in recent_execution_lines)
        if healthy_trace_count >= 1:
            suggestions.append(
                OptimizationSuggestion(
                    category="efficiency",
                    priority="low",
                    title="Use healthy runs to reduce wasted attention",
                    rationale="Execution logs show healthy-state confirmations, which means the loop is spending cycles validating a stable system.",
                    proposed_action="Create a trusted task registry so healthy runs can trigger lightweight optimization work instead of only no-op verification.",
                )
            )

        # 4. Track decision consistency
        ok_count = sum(str(d.get("overall_state", "")).upper() == "OK" for d in recent_decisions)
        if ok_count >= 1:
            suggestions.append(
                OptimizationSuggestion(
                    category="metrics",
                    priority="medium",
                    title="Add a weekly autonomy scorecard",
                    rationale="Now that decisions and execution are stable, the project needs a measurable way to judge improvement over time.",
                    proposed_action="Create weekly scores for reliability, autonomy, proactivity, and repeat-failure reduction.",
                )
            )

        # 5. If no suggestions somehow, keep one minimal recommendation
        if not suggestions:
            suggestions.append(
                OptimizationSuggestion(
                    category="baseline",
                    priority="low",
                    title="Maintain current control loop",
                    rationale="No immediate optimization pattern was detected from the current inputs.",
                    proposed_action="Continue the existing decision-execution-verification cadence and gather more history for trend analysis.",
                )
            )

        return suggestions[:5]

    def _build_summary(
        self,
        overall_state: str,
        confidence: str,
        recent_decisions: List[Dict[str, Any]],
        suggestions: List[OptimizationSuggestion],
    ) -> Dict[str, Any]:
        ok_count = sum(str(d.get("overall_state", "")).upper() == "OK" for d in recent_decisions)
        warn_count = sum(str(d.get("overall_state", "")).upper() == "WARN" for d in recent_decisions)
        fail_count = sum(str(d.get("overall_state", "")).upper() == "FAIL" for d in recent_decisions)

        return {
            "current_mode": "stable" if overall_state == "OK" and confidence == "HIGH" else "recovering",
            "recent_ok_runs": ok_count,
            "recent_warn_runs": warn_count,
            "recent_fail_runs": fail_count,
            "top_recommendation": suggestions[0].title if suggestions else "None",
        }

    def _write_report(self, output: Dict[str, Any]) -> None:
        lines = [
            "# Optimization Report",
            f"- Generated (Local): {output.get('generated_local', '')}",
            f"- Generated (UTC): {output.get('generated_utc', '')}",
            f"- Overall State Seen: {output.get('overall_state_seen', '')}",
            f"- Confidence Seen: {output.get('confidence_seen', '')}",
            "",
            "## Summary",
        ]

        summary = output.get("summary", {})
        for key in ["current_mode", "recent_ok_runs", "recent_warn_runs", "recent_fail_runs", "top_recommendation"]:
            lines.append(f"- {key}: {summary.get(key, '')}")

        lines.extend(["", "## Suggestions"])

        for idx, item in enumerate(output.get("suggestions", []), start=1):
            lines.extend([
                f"### {idx}. {item.get('title', '')}",
                f"- Category: {item.get('category', '')}",
                f"- Priority: {item.get('priority', '')}",
                f"- Rationale: {item.get('rationale', '')}",
                f"- Proposed Action: {item.get('proposed_action', '')}",
                "",
            ])

        self.report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _write_json(self, today: str, output: Dict[str, Any]) -> None:
        path = self.optimization_dir / f"{today}_optimization.json"
        path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    def _append_audit_log(self, output: Dict[str, Any]) -> None:
        stamp = output.get("generated_utc", "")
        summary = output.get("summary", {})
        line = (
            f"{stamp} "
            f"mode={summary.get('current_mode', '')} "
            f"ok_runs={summary.get('recent_ok_runs', '')} "
            f"warn_runs={summary.get('recent_warn_runs', '')} "
            f"fail_runs={summary.get('recent_fail_runs', '')} "
            f"top_recommendation={summary.get('top_recommendation', '')}\n"
        )
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe optimization layer for AI Consensus System.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory")
    parser.add_argument("--repo-root", default="/home/rafa1215/consensus-project")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = OptimizationAgent(
        mem_root=Path(args.mem_root),
        repo_root=Path(args.repo_root),
        dry_run=args.dry_run,
    )
    output = agent.run()
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())