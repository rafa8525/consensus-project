#!/usr/bin/env python3
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional


MAX_AGE_S = int(os.environ.get("CORE_MONITORS_MAX_AGE_S", str(36 * 3600)))

CANONICAL_MEM_ROOT = Path("/home/rafa1215/memory")
REPO_MEM_ROOT = Path("/home/rafa1215/consensus-project/memory")

OUTPUT_SNAPSHOT_CANONICAL = CANONICAL_MEM_ROOT / "logs/status/system_health_snapshot.md"
OUTPUT_SNAPSHOT_REPO = REPO_MEM_ROOT / "logs/status/system_health_snapshot.md"


@dataclass
class CheckResult:
    label: str
    status: str
    notes: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def fmt_age(age_s: float) -> str:
    days = age_s / 86400.0
    hours = age_s / 3600.0
    if days >= 1:
        return f"{days:.1f}d old"
    return f"{hours:.1f}h old"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def file_mtime(path: Path) -> Optional[float]:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None
    except OSError:
        return None


def newest_existing(paths: Iterable[Path]) -> Optional[tuple[Path, float]]:
    best_path: Optional[Path] = None
    best_mtime: Optional[float] = None

    for path in paths:
        mtime = file_mtime(path)
        if mtime is None:
            continue
        if best_mtime is None or mtime > best_mtime:
            best_path = path
            best_mtime = mtime

    if best_path is None or best_mtime is None:
        return None
    return best_path, best_mtime


def ok_if_recent_any(
    label: str,
    candidate_paths: List[Path],
    max_age_s: int,
    now_ts: float,
) -> CheckResult:
    best = newest_existing(candidate_paths)
    if best is None:
        first = candidate_paths[0] if candidate_paths else "<no paths>"
        return CheckResult(label=label, status="warn", notes=f"missing: {first}")

    best_path, best_mtime = best
    age_s = now_ts - best_mtime
    if age_s <= max_age_s:
        return CheckResult(label=label, status="ok", notes=f"recent: {best_path}")
    return CheckResult(
        label=label,
        status="warn",
        notes=f"stale ({fmt_age(age_s)}): {best_path}",
    )


def status_roots() -> List[Path]:
    return [
        CANONICAL_MEM_ROOT / "logs/status",
        REPO_MEM_ROOT / "logs/status",
    ]


def system_roots() -> List[Path]:
    return [
        CANONICAL_MEM_ROOT / "logs/system",
        REPO_MEM_ROOT / "logs/system",
    ]


def candidate_paths(*relative_paths: str) -> List[Path]:
    paths: List[Path] = []
    for rel in relative_paths:
        rel = rel.strip("/")
        if rel.startswith("logs/status/"):
            suffix = rel[len("logs/status/") :]
            for root in status_roots():
                paths.append(root / suffix)
        elif rel.startswith("logs/system/"):
            suffix = rel[len("logs/system/") :]
            for root in system_roots():
                paths.append(root / suffix)
        else:
            for root in system_roots():
                paths.append(root / rel)
            for root in status_roots():
                paths.append(root / rel)
    return paths


def build_checks(now_ts: float) -> List[CheckResult]:
    today_utc = utc_now().strftime("%Y-%m-%d")
    checks: List[CheckResult] = []

    checks.append(
        ok_if_recent_any(
            "absorb_runner",
            candidate_paths(
                "logs/status/absorption_status.md",
                "logs/system/absorption_timestamp.log",
                "logs/system/absorb_runner.log",
                "logs/system/absorb_memory.log",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "absorb_status_report",
            candidate_paths(
                "logs/status/absorption_status.md",
                "logs/system/absorption_monitor.jsonl",
                "logs/system/knowledge_base_status.log",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "geofence_heartbeat",
            candidate_paths(
                "logs/system/heartbeat.md",
                "logs/system/geofence_heartbeat.md",
                "logs/system/heartbeat.log",
                "logs/system/geofence_sms_monitor.jsonl",
                "logs/system/voice_trigger_heartbeat.log",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "gmail_refresh_guard_v3",
            candidate_paths(
                "logs/system/gmail_status.md",
                "logs/system/gmail_refresh_guard.log",
                "logs/system/gmail_refresh_guard_v3.log",
                "logs/system/gmail_monitor.jsonl",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "generate_status_report",
            candidate_paths(
                "logs/system/weekly_status_report.txt",
                "logs/status/weekly_status_report.md",
                f"logs/system/status_report_{today_utc}.md",
                "logs/system/status_report_latest.md",
                "logs/system/project_status/latest_status_report.md",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "movies_monitor",
            candidate_paths(
                "logs/system/movies_monitor_status.json",
                "logs/status/movie_list_status.md",
                "logs/system/movies_monitor.log",
                "logs/system/movie_sync/movie_list_status.md",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_any(
            "agents_orchestrator",
            candidate_paths(
                "logs/status/agent_orchestrator_status.md",
                "logs/system/master_control_loop.log",
                "logs/system/master_control_loop.out",
                "logs/system/agent_self_repair.log",
                "logs/system/agent_evolution_cycle.log",
                "logs/system/master_guard_integrator.log",
                "logs/system/phase4_agent_orchestrator.log",
            ),
            max_age_s=MAX_AGE_S,
            now_ts=now_ts,
        )
    )

    return checks


def overall_status(checks: List[CheckResult]) -> str:
    return "warn" if any(c.status != "ok" for c in checks) else "ok"


def build_snapshot_text(checks: List[CheckResult]) -> str:
    now = utc_now().isoformat()
    lines = [
        "# System Health Snapshot",
        f"- Generated: {now}",
        "- Dry run: false",
        "- Agent: core_monitors_bundle.py replacement-v2026-03-23-path-sync",
        f"- mem_root: {CANONICAL_MEM_ROOT}",
        "| Subsystem | Status | Notes |",
        "|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.label} | {c.status} | {c.notes} |")
    lines.append(f"- Overall: {overall_status(checks)}")
    return "\n".join(lines) + "\n"


def write_snapshot(text: str) -> None:
    ensure_parent(OUTPUT_SNAPSHOT_CANONICAL)
    OUTPUT_SNAPSHOT_CANONICAL.write_text(text)

    try:
        ensure_parent(OUTPUT_SNAPSHOT_REPO)
        OUTPUT_SNAPSHOT_REPO.write_text(text)
    except OSError:
        pass


def main() -> int:
    now_ts = time.time()
    checks = build_checks(now_ts)
    snapshot = build_snapshot_text(checks)
    write_snapshot(snapshot)
    print(snapshot, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())