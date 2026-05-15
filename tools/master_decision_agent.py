#!/usr/bin/env python3
"""
master_decision_agent.py

Purpose:
- Read key system signals from Rafael's AI Consensus System
- Normalize the signals into a simple state model
- Produce one short daily decision brief
- Produce one machine-readable JSON artifact
- Produce one audit log line per run

Design goals:
- Safe first-pass implementation
- File-based only
- No external API dependencies
- Easy to simulate and verify
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
class Signal:
    name: str
    status: str  # ok | warn | fail | unknown
    detail: str
    age_hours: Optional[float] = None
    source_path: Optional[str] = None


@dataclass
class DecisionOutput:
    generated_local: str
    generated_utc: str
    overall_state: str
    confidence: str
    top_actions: List[str]
    top_risk: str
    top_optimization: str
    evidence: List[Dict[str, Any]]


class MasterDecisionAgent:
    def __init__(self, mem_root: Path, repo_root: Path, dry_run: bool = False) -> None:
        self.mem_root = mem_root
        self.repo_root = repo_root
        self.dry_run = dry_run

        self.status_dir = self.mem_root / "logs" / "status"
        self.decisions_dir = self.mem_root / "logs" / "decisions"
        self.prevention_dir = self.mem_root / "logs" / "prevention"
        self.fitness_dir = self.mem_root / "logs" / "fitness"
        self.finance_dir = self.mem_root / "logs" / "finance"
        self.system_dir = self.mem_root / "logs" / "system"
        self.predictions_dir = self.system_dir / "predictions"

        self.brief_path = self.status_dir / "master_decision_brief.md"
        self.audit_path = self.decisions_dir / "decision_audit.log"

    def run(self) -> DecisionOutput:
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)
        today_local = now_local.date().isoformat()

        self._ensure_dirs()

        signals = [
            self._read_system_health_signal(now_utc),
            self._read_prediction_feed_signal(now_utc, today_local),
            self._read_fitness_signal(today_local, now_utc),
            self._read_finance_signal(now_utc),
            self._read_vpn_signal(now_utc),
            self._read_prevention_signal(now_utc),
        ]

        overall_state = self._compute_overall_state(signals)
        confidence = self._compute_confidence(signals)
        top_actions = self._build_top_actions(signals)
        top_risk = self._build_top_risk(signals)
        top_optimization = self._build_top_optimization(signals)

        output = DecisionOutput(
            generated_local=now_local.isoformat(),
            generated_utc=now_utc.isoformat(),
            overall_state=overall_state,
            confidence=confidence,
            top_actions=top_actions[:3],
            top_risk=top_risk,
            top_optimization=top_optimization,
            evidence=[asdict(s) for s in signals],
        )

        if not self.dry_run:
            self._write_markdown_brief(output)
            self._write_json_output(output, today_local)
            self._append_audit_log(output)

        return output

    def _ensure_dirs(self) -> None:
        for path in [
            self.status_dir,
            self.decisions_dir,
            self.prevention_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def _read_system_health_signal(self, now_utc: datetime) -> Signal:
        path = self.status_dir / "system_health_snapshot.md"
        if not path.exists():
            return Signal(
                name="system_health_snapshot",
                status="fail",
                detail="missing system health snapshot",
                source_path=str(path),
            )

        text = self._safe_read_text(path)
        age_hours = self._file_age_hours(path, now_utc)

        if "overall: ok" in text.lower():
            base_status = "ok"
        elif "warn" in text.lower():
            base_status = "warn"
        elif "fail" in text.lower():
            base_status = "fail"
        else:
            base_status = "unknown"

        if age_hours is not None:
            if age_hours > 24:
                status = "fail"
                detail = f"stale system health snapshot ({age_hours:.1f}h old)"
            elif age_hours > 8:
                status = "warn"
                detail = f"aging system health snapshot ({age_hours:.1f}h old)"
            else:
                status = base_status
                detail = f"system health snapshot fresh ({age_hours:.1f}h old)"
        else:
            status = "unknown"
            detail = "unable to determine age of system health snapshot"

        return Signal(
            name="system_health_snapshot",
            status=status,
            detail=detail,
            age_hours=age_hours,
            source_path=str(path),
        )

    def _read_prediction_feed_signal(self, now_utc: datetime, today_local: str) -> Signal:
        today_path = self.predictions_dir / f"prediction_feed_{today_local}.md"
        if today_path.exists():
            age_hours = self._file_age_hours(today_path, now_utc)
            return Signal(
                name="prediction_feed",
                status="ok" if (age_hours is not None and age_hours <= 24) else "warn",
                detail=f"today's prediction feed present ({age_hours:.1f}h old)" if age_hours is not None else "today's prediction feed present",
                age_hours=age_hours,
                source_path=str(today_path),
            )

        latest = self._find_latest_file(self.predictions_dir, "prediction_feed_*.md")
        if latest is None:
            return Signal(
                name="prediction_feed",
                status="warn",
                detail="no prediction feed found",
                source_path=str(self.predictions_dir),
            )

        age_hours = self._file_age_hours(latest, now_utc)
        if age_hours is not None and age_hours > 48:
            status = "fail"
            detail = f"prediction feed stale ({age_hours:.1f}h old)"
        else:
            status = "warn"
            detail = f"today's prediction feed missing; latest is {age_hours:.1f}h old" if age_hours is not None else "today's prediction feed missing"

        return Signal(
            name="prediction_feed",
            status=status,
            detail=detail,
            age_hours=age_hours,
            source_path=str(latest),
        )

    def _read_fitness_signal(self, today_local: str, now_utc: datetime) -> Signal:
        today_path = self.fitness_dir / f"daily_{today_local}.md"
        if today_path.exists():
            age_hours = self._file_age_hours(today_path, now_utc)
            return Signal(
                name="fitness_log",
                status="ok",
                detail="fitness log present for today",
                age_hours=age_hours,
                source_path=str(today_path),
            )

        latest = self._find_latest_file(self.fitness_dir, "daily_*.md")
        if latest is None:
            return Signal(
                name="fitness_log",
                status="warn",
                detail="no fitness logs found",
                source_path=str(self.fitness_dir),
            )

        age_hours = self._file_age_hours(latest, now_utc)
        return Signal(
            name="fitness_log",
            status="warn",
            detail=f"no fitness log for today; latest is {age_hours:.1f}h old" if age_hours is not None else "no fitness log for today",
            age_hours=age_hours,
            source_path=str(latest),
        )

    def _read_finance_signal(self, now_utc: datetime) -> Signal:
        latest = self._find_latest_file(self.finance_dir, "*.md")
        if latest is None:
            return Signal(
                name="finance_log",
                status="warn",
                detail="no finance logs found",
                source_path=str(self.finance_dir),
            )

        age_hours = self._file_age_hours(latest, now_utc)
        if age_hours is None:
            return Signal(
                name="finance_log",
                status="unknown",
                detail="finance log exists but age is unknown",
                source_path=str(latest),
            )

        if age_hours > 24 * 7:
            status = "fail"
            detail = f"finance log stale ({age_hours / 24:.1f} days old)"
        elif age_hours > 24 * 3:
            status = "warn"
            detail = f"finance log aging ({age_hours / 24:.1f} days old)"
        else:
            status = "ok"
            detail = f"finance log recent ({age_hours / 24:.1f} days old)"

        return Signal(
            name="finance_log",
            status=status,
            detail=detail,
            age_hours=age_hours,
            source_path=str(latest),
        )

    def _read_vpn_signal(self, now_utc: datetime) -> Signal:
        candidates = [
            self.status_dir / "vpn_status.md",
            self.system_dir / "vpn_status.md",
            self.system_dir / "vpn_status.json",
        ]

        existing = next((p for p in candidates if p.exists()), None)
        if existing is None:
            return Signal(
                name="vpn_status",
                status="unknown",
                detail="vpn status file not found",
                source_path=" | ".join(str(p) for p in candidates),
            )

        age_hours = self._file_age_hours(existing, now_utc)
        text = self._safe_read_text(existing)

        lowered = text.lower()
        if "public wifi" in lowered and "off" in lowered:
            status = "fail"
            detail = "vpn appears off on public wifi"
        elif "on" in lowered or '"status": "on"' in lowered or '"vpn": "on"' in lowered:
            status = "ok"
            detail = "vpn status indicates on"
        else:
            status = "warn"
            detail = "vpn status exists but state is unclear"

        if age_hours is not None and age_hours > 72:
            status = "warn" if status == "ok" else status
            detail += f"; status file is stale ({age_hours:.1f}h old)"

        return Signal(
            name="vpn_status",
            status=status,
            detail=detail,
            age_hours=age_hours,
            source_path=str(existing),
        )

    def _read_prevention_signal(self, now_utc: datetime) -> Signal:
        index_path = self.prevention_dir / "prevention_index.md"
        if not index_path.exists():
            return Signal(
                name="prevention_memory",
                status="warn",
                detail="prevention index missing",
                source_path=str(index_path),
            )

        age_hours = self._file_age_hours(index_path, now_utc)
        return Signal(
            name="prevention_memory",
            status="ok",
            detail="prevention index present",
            age_hours=age_hours,
            source_path=str(index_path),
        )

    def _compute_overall_state(self, signals: List[Signal]) -> str:
        statuses = {s.status for s in signals}
        if "fail" in statuses:
            return "FAIL"
        if "warn" in statuses or "unknown" in statuses:
            return "WARN"
        return "OK"

    def _compute_confidence(self, signals: List[Signal]) -> str:
        score = 100
        for s in signals:
            if s.status == "fail":
                score -= 30
            elif s.status == "warn":
                score -= 15
            elif s.status == "unknown":
                score -= 10

        if score >= 80:
            return "HIGH"
        if score >= 55:
            return "MEDIUM"
        return "LOW"

    def _build_top_actions(self, signals: List[Signal]) -> List[str]:
        actions: List[str] = []

        by_name = {s.name: s for s in signals}

        health = by_name.get("system_health_snapshot")
        if health and health.status in {"warn", "fail"}:
            actions.append("Review and refresh the system health monitor pipeline")

        pred = by_name.get("prediction_feed")
        if pred and pred.status in {"warn", "fail"}:
            actions.append("Regenerate the prediction feed so today has a fresh decision context")

        fitness = by_name.get("fitness_log")
        if fitness and fitness.status in {"warn", "fail"}:
            actions.append("Log today’s fitness activity or trigger the fitness prompt flow")

        finance = by_name.get("finance_log")
        if finance and finance.status in {"warn", "fail"}:
            actions.append("Create or update a finance log entry to keep weekly tracking alive")

        vpn = by_name.get("vpn_status")
        if vpn and vpn.status in {"warn", "fail", "unknown"}:
            actions.append("Verify VPN detection and write a fresh VPN status marker")

        prevention = by_name.get("prevention_memory")
        if prevention and prevention.status in {"warn", "fail"}:
            actions.append("Create the prevention index so recurring failures can be learned once")

        if not actions:
            actions.append("No immediate remediation needed; maintain normal monitoring cadence")

        return actions

    def _build_top_risk(self, signals: List[Signal]) -> str:
        priority = ["fail", "warn", "unknown", "ok"]
        ranked = sorted(signals, key=lambda s: priority.index(s.status))
        top = ranked[0]
        return f"{top.name}: {top.detail}"

    def _build_top_optimization(self, signals: List[Signal]) -> str:
        for s in signals:
            if s.name == "system_health_snapshot" and s.status in {"warn", "fail"}:
                return "Convert stale-status detection into an automatic remediation workflow"
            if s.name == "fitness_log" and s.status in {"warn", "fail"}:
                return "Turn missing daily fitness logs into a same-day coaching and reminder loop"
            if s.name == "vpn_status" and s.status in {"warn", "fail", "unknown"}:
                return "Add a VPN heartbeat that writes current network type and VPN state every run"

        return "Use this daily decision brief as the central control layer for all subsystem outputs"

    def _write_markdown_brief(self, output: DecisionOutput) -> None:
        lines = [
            "# Master Decision Brief",
            f"- Generated (Local): {output.generated_local}",
            f"- Generated (UTC): {output.generated_utc}",
            f"- Overall State: {output.overall_state}",
            f"- Confidence: {output.confidence}",
            "",
            "## Top Actions",
        ]

        for idx, action in enumerate(output.top_actions, start=1):
            lines.append(f"{idx}. {action}")

        lines.extend([
            "",
            "## Top Risk",
            f"- {output.top_risk}",
            "",
            "## Top Optimization",
            f"- {output.top_optimization}",
            "",
            "## Evidence",
        ])

        for item in output.evidence:
            name = item["name"]
            status = item["status"]
            detail = item["detail"]
            source_path = item.get("source_path") or "n/a"
            age_hours = item.get("age_hours")
            age_txt = f"{age_hours:.1f}h" if isinstance(age_hours, (int, float)) else "n/a"
            lines.append(f"- {name}: {status} | {detail} | age={age_txt} | source={source_path}")

        self.brief_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_json_output(self, output: DecisionOutput, today_local: str) -> None:
        out_path = self.decisions_dir / f"{today_local}_decision.json"
        out_path.write_text(json.dumps(asdict(output), indent=2), encoding="utf-8")

    def _append_audit_log(self, output: DecisionOutput) -> None:
        line = (
            f"{output.generated_utc} "
            f"overall={output.overall_state} "
            f"confidence={output.confidence} "
            f"actions={len(output.top_actions)}\n"
        )
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(line)

    def _safe_read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return f"read_error: {exc}"

    def _file_age_hours(self, path: Path, now_utc: datetime) -> Optional[float]:
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            return (now_utc - mtime).total_seconds() / 3600.0
        except Exception:
            return None

    def _find_latest_file(self, directory: Path, pattern: str) -> Optional[Path]:
        if not directory.exists():
            return None
        matches = list(directory.glob(pattern))
        if not matches:
            return None
        return max(matches, key=lambda p: p.stat().st_mtime)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a master decision brief for the AI Consensus System.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory", help="Path to memory root")
    parser.add_argument("--repo-root", default="/home/rafa1215/consensus-project", help="Path to repository root")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = MasterDecisionAgent(
        mem_root=Path(args.mem_root),
        repo_root=Path(args.repo_root),
        dry_run=args.dry_run,
    )
    output = agent.run()
    print(json.dumps(asdict(output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())