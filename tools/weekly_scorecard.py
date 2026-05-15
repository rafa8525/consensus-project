#!/usr/bin/env python3
"""
weekly_scorecard.py

Purpose:
- Generate a weekly project scorecard for Rafael's AI Consensus System
- Measure reliability, autonomy, proactivity, and freshness
- Write a human-readable markdown report
- Write a machine-readable JSON artifact
- Append a small audit line

Version 1 principles:
- file-based only
- no destructive behavior
- uses existing logs and decision artifacts
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


@dataclass
class ScoreMetric:
    name: str
    value: float
    max_value: float
    display: str
    rationale: str


class WeeklyScorecard:
    def __init__(self, mem_root: Path, repo_root: Path, dry_run: bool = False) -> None:
        self.mem_root = mem_root
        self.repo_root = repo_root
        self.dry_run = dry_run

        self.decisions_dir = self.mem_root / "logs" / "decisions"
        self.optimization_dir = self.mem_root / "logs" / "optimization"
        self.system_exec_dir = self.mem_root / "logs" / "system" / "exec"
        self.status_dir = self.mem_root / "logs" / "status"
        self.scorecard_dir = self.mem_root / "logs" / "scorecards"

        self.audit_path = self.system_exec_dir / "weekly_scorecard_audit.log"
        self.report_path = self.scorecard_dir / "weekly_scorecard.md"

    def run(self) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)
        start_local = now_local - timedelta(days=7)

        self._ensure_dirs()

        decisions = self._load_recent_decisions(start_local)
        optimization_files = self._load_recent_optimization_files(start_local)
        execution_lines = self._read_recent_lines(
            self.system_exec_dir / "execution_agent_audit.log",
            limit=300,
        )
        remediation_lines = self._read_recent_lines(
            self.system_exec_dir / "auto_remediation_audit.log",
            limit=300,
        )

        metrics = self._build_metrics(
            decisions=decisions,
            optimization_files=optimization_files,
            execution_lines=execution_lines,
            remediation_lines=remediation_lines,
        )

        total_score = round(sum(m.value for m in metrics), 1)
        max_score = round(sum(m.max_value for m in metrics), 1)
        percentage = round((total_score / max_score) * 100, 1) if max_score else 0.0
        trend = self._derive_trend(metrics)

        output = {
            "generated_local": now_local.isoformat(),
            "generated_utc": now_utc.isoformat(),
            "window_start_local": start_local.isoformat(),
            "window_end_local": now_local.isoformat(),
            "summary": {
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "trend": trend,
                "grade": self._grade_from_percentage(percentage),
            },
            "metrics": [asdict(m) for m in metrics],
        }

        if not self.dry_run:
            self._write_markdown(output)
            self._write_json(now_local.date().isoformat(), output)
            self._append_audit_log(output)

        return output

    def _ensure_dirs(self) -> None:
        self.scorecard_dir.mkdir(parents=True, exist_ok=True)
        self.system_exec_dir.mkdir(parents=True, exist_ok=True)

    def _load_recent_decisions(self, start_local: datetime) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for path in sorted(self.decisions_dir.glob("*_decision.json")):
            data = self._read_json(path)
            ts = self._parse_dt(data.get("generated_local"))
            if ts and ts >= start_local:
                results.append(data)
        return results

    def _load_recent_optimization_files(self, start_local: datetime) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for path in sorted(self.optimization_dir.glob("*_optimization.json")):
            data = self._read_json(path)
            ts = self._parse_dt(data.get("generated_local"))
            if ts and ts >= start_local:
                results.append(data)
        return results

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _read_recent_lines(self, path: Path, limit: int = 300) -> List[str]:
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            return lines[-limit:]
        except Exception:
            return []

    def _parse_dt(self, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def _build_metrics(
        self,
        decisions: List[Dict[str, Any]],
        optimization_files: List[Dict[str, Any]],
        execution_lines: List[str],
        remediation_lines: List[str],
    ) -> List[ScoreMetric]:
        metrics: List[ScoreMetric] = []

        # Reliability: how many decision runs are OK
        total_decisions = len(decisions)
        ok_runs = sum(str(d.get("overall_state", "")).upper() == "OK" for d in decisions)
        reliability_pct = (ok_runs / total_decisions * 100.0) if total_decisions else 0.0
        reliability_score = round(reliability_pct / 20.0, 1)  # 0-5
        metrics.append(
            ScoreMetric(
                name="reliability",
                value=min(reliability_score, 5.0),
                max_value=5.0,
                display=f"{reliability_pct:.1f}% OK runs ({ok_runs}/{total_decisions})" if total_decisions else "No decision history yet",
                rationale="Measures how consistently the system reaches overall OK state.",
            )
        )

        # Autonomy: healthy traces + low manual-style repair footprint
        healthy_traces = sum("name=healthy_state_trace status=executed" in line for line in execution_lines)
        remediation_executed = sum("status=applied" in line for line in remediation_lines)
        autonomy_raw = min(healthy_traces + 1, 5)
        if remediation_executed > healthy_traces and remediation_executed > 0:
            autonomy_raw = max(1, autonomy_raw - 1)
        metrics.append(
            ScoreMetric(
                name="autonomy",
                value=float(autonomy_raw),
                max_value=5.0,
                display=f"healthy_traces={healthy_traces}, remediations={remediation_executed}",
                rationale="Rewards healthy autonomous cycles and lightly penalizes frequent repair dependence.",
            )
        )

        # Proactivity: optimization suggestions exist and are being generated
        suggestion_count = 0
        for item in optimization_files:
            suggestions = item.get("suggestions", [])
            if isinstance(suggestions, list):
                suggestion_count += len(suggestions)
        proactivity_score = min(5.0, round(suggestion_count / 2.0, 1))
        metrics.append(
            ScoreMetric(
                name="proactivity",
                value=proactivity_score,
                max_value=5.0,
                display=f"{suggestion_count} optimization suggestions in window",
                rationale="Measures whether the system is producing forward-looking improvements, not just repairs.",
            )
        )

        # Freshness: average age of key evidence at decision time
        avg_prediction_age = self._average_evidence_age(decisions, "prediction_feed")
        avg_health_age = self._average_evidence_age(decisions, "system_health_snapshot")
        freshness_score = self._freshness_score(avg_prediction_age, avg_health_age)
        metrics.append(
            ScoreMetric(
                name="freshness",
                value=freshness_score,
                max_value=5.0,
                display=f"avg prediction age={self._fmt_age(avg_prediction_age)}, avg health age={self._fmt_age(avg_health_age)}",
                rationale="Rewards recent system signals and recent prediction context.",
            )
        )

        # Stability trend: based on mix of OK/WARN/FAIL in recent decisions
        warn_runs = sum(str(d.get("overall_state", "")).upper() == "WARN" for d in decisions)
        fail_runs = sum(str(d.get("overall_state", "")).upper() == "FAIL" for d in decisions)
        stability_value = 5.0
        stability_value -= min(2.5, warn_runs * 0.5)
        stability_value -= min(4.0, fail_runs * 1.0)
        stability_value = max(0.0, round(stability_value, 1))
        metrics.append(
            ScoreMetric(
                name="stability_trend",
                value=stability_value,
                max_value=5.0,
                display=f"OK={ok_runs}, WARN={warn_runs}, FAIL={fail_runs}",
                rationale="Captures whether the system is trending cleanly or spending time in degraded states.",
            )
        )

        return metrics

    def _average_evidence_age(self, decisions: List[Dict[str, Any]], signal_name: str) -> Optional[float]:
        ages: List[float] = []
        for decision in decisions:
            evidence = decision.get("evidence", [])
            if not isinstance(evidence, list):
                continue
            for item in evidence:
                if not isinstance(item, dict):
                    continue
                if item.get("name") == signal_name and isinstance(item.get("age_hours"), (int, float)):
                    ages.append(float(item["age_hours"]))
        if not ages:
            return None
        return sum(ages) / len(ages)

    def _freshness_score(self, avg_prediction_age: Optional[float], avg_health_age: Optional[float]) -> float:
        score = 5.0

        if avg_prediction_age is not None:
            if avg_prediction_age > 12:
                score -= 3.0
            elif avg_prediction_age > 6:
                score -= 2.0
            elif avg_prediction_age > 4:
                score -= 1.0

        if avg_health_age is not None:
            if avg_health_age > 24:
                score -= 3.0
            elif avg_health_age > 8:
                score -= 2.0
            elif avg_health_age > 2:
                score -= 1.0

        return max(0.0, round(score, 1))

    def _fmt_age(self, value: Optional[float]) -> str:
        if value is None:
            return "n/a"
        return f"{value:.1f}h"

    def _derive_trend(self, metrics: List[ScoreMetric]) -> str:
        total = sum(m.value for m in metrics)
        if total >= 22:
            return "strong"
        if total >= 16:
            return "stable"
        if total >= 10:
            return "mixed"
        return "recovering"

    def _grade_from_percentage(self, pct: float) -> str:
        if pct >= 90:
            return "A"
        if pct >= 80:
            return "B"
        if pct >= 70:
            return "C"
        if pct >= 60:
            return "D"
        return "F"

    def _write_markdown(self, output: Dict[str, Any]) -> None:
        summary = output["summary"]
        lines = [
            "# Weekly Scorecard",
            f"- Generated (Local): {output['generated_local']}",
            f"- Generated (UTC): {output['generated_utc']}",
            f"- Window Start (Local): {output['window_start_local']}",
            f"- Window End (Local): {output['window_end_local']}",
            "",
            "## Summary",
            f"- Total Score: {summary['total_score']} / {summary['max_score']}",
            f"- Percentage: {summary['percentage']}%",
            f"- Grade: {summary['grade']}",
            f"- Trend: {summary['trend']}",
            "",
            "## Metrics",
        ]

        for item in output["metrics"]:
            lines.extend([
                f"### {item['name']}",
                f"- Score: {item['value']} / {item['max_value']}",
                f"- Detail: {item['display']}",
                f"- Rationale: {item['rationale']}",
                "",
            ])

        self.report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _write_json(self, today: str, output: Dict[str, Any]) -> None:
        path = self.scorecard_dir / f"{today}_weekly_scorecard.json"
        path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    def _append_audit_log(self, output: Dict[str, Any]) -> None:
        summary = output["summary"]
        line = (
            f"{output['generated_utc']} "
            f"score={summary['total_score']}/{summary['max_score']} "
            f"pct={summary['percentage']} "
            f"grade={summary['grade']} "
            f"trend={summary['trend']}\n"
        )
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weekly scorecard for AI Consensus System.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory")
    parser.add_argument("--repo-root", default="/home/rafa1215/consensus-project")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
        args = parse_args()
        runner = WeeklyScorecard(
            mem_root=Path(args.mem_root),
            repo_root=Path(args.repo_root),
            dry_run=args.dry_run,
        )
        output = runner.run()
        print(json.dumps(output, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())