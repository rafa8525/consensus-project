#!/usr/bin/env python3
"""
core_system_runner.py

Purpose:
- Create one single source of truth for project health
- Read the latest project artifacts
- Apply freshness and presence rules
- Write:
    1) /home/rafa1215/memory/system_master_status.json
    2) /home/rafa1215/memory/logs/status/daily_system_report.md
    3) /home/rafa1215/memory/logs/system/exec/core_system_runner_audit.log

Design:
- Safe
- File-based
- No destructive actions
- No external dependencies
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("America/Los_Angeles")


@dataclass
class SubsystemResult:
    name: str
    status: str   # OK | WARN | FAIL | UNKNOWN
    detail: str
    age_hours: Optional[float]
    source_path: str


class CoreSystemRunner:
    def __init__(self, mem_root: Path, repo_root: Path, dry_run: bool = False) -> None:
        self.mem_root = mem_root
        self.repo_root = repo_root
        self.dry_run = dry_run

        self.logs_dir = self.mem_root / "logs"
        self.status_dir = self.logs_dir / "status"
        self.system_dir = self.logs_dir / "system"
        self.exec_dir = self.system_dir / "exec"
        self.decisions_dir = self.logs_dir / "decisions"
        self.optimization_dir = self.logs_dir / "optimization"
        self.scorecard_dir = self.logs_dir / "scorecards"
        self.fitness_dir = self.logs_dir / "fitness"
        self.finance_dir = self.logs_dir / "finance"
        self.prevention_dir = self.logs_dir / "prevention"

        self.master_status_path = self.mem_root / "system_master_status.json"
        self.daily_report_path = self.status_dir / "daily_system_report.md"
        self.audit_path = self.exec_dir / "core_system_runner_audit.log"

    def run(self) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(LOCAL_TZ)
        today = now_local.date().isoformat()

        self._ensure_dirs()

        results = [
            self._check_system_health_snapshot(now_utc),
            self._check_prediction_feed(now_utc, today),
            self._check_fitness_log(now_utc, today),
            self._check_finance_log(now_utc),
            self._check_vpn_status(now_utc),
            self._check_prevention_memory(now_utc),
            self._check_decision_layer(now_utc, today),
            self._check_optimization_layer(now_utc, today),
            self._check_scorecard_layer(now_utc, today),
        ]

        overall_status = self._compute_overall_status(results)

        master_status = self._build_master_status(
            now_local=now_local,
            now_utc=now_utc,
            overall_status=overall_status,
            results=results,
        )

        report_text = self._build_daily_report(
            now_local=now_local,
            now_utc=now_utc,
            overall_status=overall_status,
            results=results,
        )

        audit_line = self._build_audit_line(now_utc, overall_status, results)

        if not self.dry_run:
            self.master_status_path.write_text(json.dumps(master_status, indent=2), encoding="utf-8")
            self.daily_report_path.write_text(report_text, encoding="utf-8")
            with self.audit_path.open("a", encoding="utf-8") as fh:
                fh.write(audit_line)

        return {
            "generated_local": now_local.isoformat(),
            "generated_utc": now_utc.isoformat(),
            "overall_status": overall_status,
            "master_status_path": str(self.master_status_path),
            "daily_report_path": str(self.daily_report_path),
            "audit_path": str(self.audit_path),
            "results": [asdict(r) for r in results],
            "dry_run": self.dry_run,
        }

    def _ensure_dirs(self) -> None:
        for path in [self.status_dir, self.exec_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def _check_system_health_snapshot(self, now_utc: datetime) -> SubsystemResult:
        path = self.status_dir / "system_health_snapshot.md"
        if not path.exists():
            return self._missing("system_health_snapshot", path)

        text = self._safe_read_text(path).lower()
        age = self._file_age_hours(path, now_utc)

        if age is None:
            return self._unknown("system_health_snapshot", "unable to determine age", path)

        if age > 24:
            return SubsystemResult("system_health_snapshot", "FAIL", f"stale ({age:.1f}h old)", age, str(path))
        if age > 8:
            return SubsystemResult("system_health_snapshot", "WARN", f"aging ({age:.1f}h old)", age, str(path))

        if "overall: ok" in text:
            return SubsystemResult("system_health_snapshot", "OK", f"fresh and valid ({age:.1f}h old)", age, str(path))
        if "overall: warn" in text:
            return SubsystemResult("system_health_snapshot", "WARN", f"fresh but warning state ({age:.1f}h old)", age, str(path))
        if "overall: fail" in text:
            return SubsystemResult("system_health_snapshot", "FAIL", f"fresh but fail state ({age:.1f}h old)", age, str(path))

        return SubsystemResult("system_health_snapshot", "WARN", f"fresh but semantic status unclear ({age:.1f}h old)", age, str(path))

    def _check_prediction_feed(self, now_utc: datetime, today: str) -> SubsystemResult:
        today_path = self.system_dir / "predictions" / f"prediction_feed_{today}.md"
        if today_path.exists():
            age = self._file_age_hours(today_path, now_utc)
            if age is None:
                return self._unknown("prediction_feed", "today's feed exists but age unknown", today_path)
            if age > 24:
                return SubsystemResult("prediction_feed", "FAIL", f"today's feed stale ({age:.1f}h old)", age, str(today_path))
            if age > 6:
                return SubsystemResult("prediction_feed", "WARN", f"today's feed aging ({age:.1f}h old)", age, str(today_path))
            return SubsystemResult("prediction_feed", "OK", f"today's feed fresh ({age:.1f}h old)", age, str(today_path))

        latest = self._find_latest_file(self.system_dir / "predictions", "prediction_feed_*.md")
        if latest is None:
            return self._missing("prediction_feed", self.system_dir / "predictions")

        age = self._file_age_hours(latest, now_utc)
        if age is None:
            return self._unknown("prediction_feed", "latest feed exists but age unknown", latest)
        if age > 24:
            return SubsystemResult("prediction_feed", "FAIL", f"today missing; latest stale ({age:.1f}h old)", age, str(latest))
        return SubsystemResult("prediction_feed", "WARN", f"today missing; latest is ({age:.1f}h old)", age, str(latest))

    def _check_fitness_log(self, now_utc: datetime, today: str) -> SubsystemResult:
        path = self.fitness_dir / f"daily_{today}.md"
        if path.exists():
            age = self._file_age_hours(path, now_utc)
            return SubsystemResult("fitness_log", "OK", "today's fitness log present", age, str(path))

        latest = self._find_latest_file(self.fitness_dir, "daily_*.md")
        if latest is None:
            return self._missing("fitness_log", self.fitness_dir)

        age = self._file_age_hours(latest, now_utc)
        return SubsystemResult("fitness_log", "WARN", f"today missing; latest is ({age:.1f}h old)" if age is not None else "today missing", age, str(latest))

    def _check_finance_log(self, now_utc: datetime) -> SubsystemResult:
        latest = self._find_latest_file(self.finance_dir, "*.md")
        if latest is None:
            return self._missing("finance_log", self.finance_dir)

        age = self._file_age_hours(latest, now_utc)
        if age is None:
            return self._unknown("finance_log", "latest finance log age unknown", latest)

        if age > 24 * 7:
            return SubsystemResult("finance_log", "FAIL", f"stale ({age / 24:.1f} days old)", age, str(latest))
        if age > 24 * 3:
            return SubsystemResult("finance_log", "WARN", f"aging ({age / 24:.1f} days old)", age, str(latest))
        return SubsystemResult("finance_log", "OK", f"recent ({age / 24:.1f} days old)", age, str(latest))

    def _check_vpn_status(self, now_utc: datetime) -> SubsystemResult:
        candidates = [
            self.status_dir / "vpn_status.md",
            self.system_dir / "vpn_status.md",
            self.system_dir / "vpn_status.json",
        ]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            return self._missing("vpn_status", self.system_dir)

        age = self._file_age_hours(path, now_utc)
        text = self._safe_read_text(path).lower()

        if age is not None and age > 72:
            return SubsystemResult("vpn_status", "WARN", f"marker stale ({age:.1f}h old)", age, str(path))

        if "status: on" in text or '"status": "on"' in text or '"vpn": "on"' in text:
            return SubsystemResult("vpn_status", "OK", "vpn status indicates on", age, str(path))
        if "status: off" in text or '"status": "off"' in text or '"vpn": "off"' in text:
            return SubsystemResult("vpn_status", "WARN", "vpn status indicates off", age, str(path))

        return SubsystemResult("vpn_status", "WARN", "status marker present but unclear", age, str(path))

    def _check_prevention_memory(self, now_utc: datetime) -> SubsystemResult:
        path = self.prevention_dir / "prevention_index.md"
        if not path.exists():
            return self._missing("prevention_memory", path)

        age = self._file_age_hours(path, now_utc)
        return SubsystemResult("prevention_memory", "OK", "prevention index present", age, str(path))

    def _check_decision_layer(self, now_utc: datetime, today: str) -> SubsystemResult:
        path = self.decisions_dir / f"{today}_decision.json"
        if not path.exists():
            latest = self._find_latest_file(self.decisions_dir, "*_decision.json")
            if latest is None:
                return self._missing("decision_layer", self.decisions_dir)
            age = self._file_age_hours(latest, now_utc)
            return SubsystemResult("decision_layer", "WARN", f"today missing; latest decision exists ({age:.1f}h old)" if age is not None else "today missing", age, str(latest))

        age = self._file_age_hours(path, now_utc)
        data = self._safe_read_json(path)
        overall = str(data.get("overall_state", "UNKNOWN")).upper()

        if overall == "OK":
            return SubsystemResult("decision_layer", "OK", f"today's decision OK ({age:.1f}h old)" if age is not None else "today's decision OK", age, str(path))
        if overall == "WARN":
            return SubsystemResult("decision_layer", "WARN", f"today's decision WARN ({age:.1f}h old)" if age is not None else "today's decision WARN", age, str(path))
        if overall == "FAIL":
            return SubsystemResult("decision_layer", "FAIL", f"today's decision FAIL ({age:.1f}h old)" if age is not None else "today's decision FAIL", age, str(path))

        return SubsystemResult("decision_layer", "WARN", "today's decision exists but overall state unclear", age, str(path))

    def _check_optimization_layer(self, now_utc: datetime, today: str) -> SubsystemResult:
        path = self.optimization_dir / f"{today}_optimization.json"
        if not path.exists():
            latest = self._find_latest_file(self.optimization_dir, "*_optimization.json")
            if latest is None:
                return self._missing("optimization_layer", self.optimization_dir)
            age = self._file_age_hours(latest, now_utc)
            return SubsystemResult("optimization_layer", "WARN", f"today missing; latest optimization exists ({age:.1f}h old)" if age is not None else "today missing", age, str(latest))

        age = self._file_age_hours(path, now_utc)
        data = self._safe_read_json(path)
        suggestions = data.get("suggestions", [])
        count = len(suggestions) if isinstance(suggestions, list) else 0
        return SubsystemResult("optimization_layer", "OK", f"today's optimization present ({count} suggestions)", age, str(path))

    def _check_scorecard_layer(self, now_utc: datetime, today: str) -> SubsystemResult:
        path = self.scorecard_dir / f"{today}_weekly_scorecard.json"
        if not path.exists():
            latest = self._find_latest_file(self.scorecard_dir, "*_weekly_scorecard.json")
            if latest is None:
                return self._missing("scorecard_layer", self.scorecard_dir)
            age = self._file_age_hours(latest, now_utc)
            return SubsystemResult("scorecard_layer", "WARN", f"today missing; latest scorecard exists ({age:.1f}h old)" if age is not None else "today missing", age, str(latest))

        age = self._file_age_hours(path, now_utc)
        data = self._safe_read_json(path)
        grade = str(data.get("summary", {}).get("grade", "UNKNOWN"))
        pct = data.get("summary", {}).get("percentage")
        pct_txt = f"{pct}%" if isinstance(pct, (int, float)) else "n/a"
        return SubsystemResult("scorecard_layer", "OK", f"today's scorecard present (grade={grade}, pct={pct_txt})", age, str(path))

    def _compute_overall_status(self, results: List[SubsystemResult]) -> str:
        statuses = {r.status for r in results}
        if "FAIL" in statuses:
            return "FAIL"
        if "WARN" in statuses or "UNKNOWN" in statuses:
            return "WARN"
        return "OK"

    def _build_master_status(
        self,
        now_local: datetime,
        now_utc: datetime,
        overall_status: str,
        results: List[SubsystemResult],
    ) -> Dict[str, Any]:
        by_name = {r.name: r for r in results}

        def state(name: str) -> str:
            return by_name[name].status if name in by_name else "UNKNOWN"

        return {
            "generated_local": now_local.isoformat(),
            "generated_utc": now_utc.isoformat(),
            "last_full_run": now_local.isoformat(),
            "absorption": "UNKNOWN",
            "sms_system": "UNKNOWN",
            "prediction_feed": state("prediction_feed"),
            "fitness_log": state("fitness_log"),
            "finance_log": state("finance_log"),
            "geofence": "UNKNOWN",
            "vpn_status": state("vpn_status"),
            "prevention_memory": state("prevention_memory"),
            "decision_layer": state("decision_layer"),
            "optimization_layer": state("optimization_layer"),
            "scorecard_layer": state("scorecard_layer"),
            "system_health_snapshot": state("system_health_snapshot"),
            "overall_status": overall_status,
            "details": {r.name: asdict(r) for r in results},
        }

    def _build_daily_report(
        self,
        now_local: datetime,
        now_utc: datetime,
        overall_status: str,
        results: List[SubsystemResult],
    ) -> str:
        by_name = {r.name: r for r in results}

        def line(name: str, label: str) -> List[str]:
            item = by_name.get(name)
            if item is None:
                return [f"- {label}: UNKNOWN"]
            age_txt = f" ({item.age_hours:.1f}h old)" if isinstance(item.age_hours, (int, float)) else ""
            return [f"- {label}: {item.status} — {item.detail}{age_txt}"]

        next_action = self._derive_next_action(results, overall_status)

        lines = [
            "# Daily System Report",
            f"- Generated (Local): {now_local.isoformat()}",
            f"- Generated (UTC): {now_utc.isoformat()}",
            f"- Overall Status: {overall_status}",
            "",
            "## Core Checks",
        ]
        lines += line("system_health_snapshot", "System Health")
        lines += line("prediction_feed", "Prediction Feed")
        lines += line("fitness_log", "Fitness")
        lines += line("finance_log", "Finance")
        lines += line("vpn_status", "VPN")
        lines += line("prevention_memory", "Prevention Memory")
        lines += line("decision_layer", "Decision Layer")
        lines += line("optimization_layer", "Optimization Layer")
        lines += line("scorecard_layer", "Scorecard Layer")
        lines += [
            "",
            "## Next Action",
            f"- {next_action}",
            "",
        ]
        return "\n".join(lines)

    def _derive_next_action(self, results: List[SubsystemResult], overall_status: str) -> str:
        if overall_status == "OK":
            return "No action needed"
        for item in results:
            if item.status == "FAIL":
                return f"Address failing subsystem: {item.name}"
        for item in results:
            if item.status == "WARN":
                return f"Review warning subsystem: {item.name}"
        return "Review system state"

    def _build_audit_line(self, now_utc: datetime, overall_status: str, results: List[SubsystemResult]) -> str:
        fail_count = sum(r.status == "FAIL" for r in results)
        warn_count = sum(r.status == "WARN" for r in results)
        ok_count = sum(r.status == "OK" for r in results)
        return (
            f"{now_utc.isoformat()} "
            f"script=core_system_runner.py "
            f"result=SUCCESS "
            f"overall={overall_status} "
            f"ok={ok_count} warn={warn_count} fail={fail_count}\n"
        )

    def _missing(self, name: str, path: Path) -> SubsystemResult:
        return SubsystemResult(name, "WARN", "missing", None, str(path))

    def _unknown(self, name: str, detail: str, path: Path) -> SubsystemResult:
        return SubsystemResult(name, "UNKNOWN", detail, None, str(path))

    def _safe_read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""

    def _safe_read_json(self, path: Path) -> Dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

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
    parser = argparse.ArgumentParser(description="Write master system status and daily report.")
    parser.add_argument("--mem-root", default="/home/rafa1215/memory")
    parser.add_argument("--repo-root", default="/home/rafa1215/consensus-project")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runner = CoreSystemRunner(
        mem_root=Path(args.mem_root),
        repo_root=Path(args.repo_root),
        dry_run=args.dry_run,
    )
    output = runner.run()
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())