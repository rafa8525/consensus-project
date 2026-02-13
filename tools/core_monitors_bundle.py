#!/usr/bin/env python3
"""
core_monitors_bundle.py

Creates a lightweight, deterministic system health snapshot.

Outputs (canonical):
  /home/rafa1215/memory/logs/status/system_health_snapshot.md

Also mirrors the same snapshot into the repo (for GitHub visibility):
  <repo_root>/memory/logs/status/system_health_snapshot.md

Design goals:
- Safe to run frequently (idempotent, small file, no noisy diffs beyond timestamps)
- No external dependencies
- Clear, minimal checks that reflect whether core subsystems are producing fresh logs
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Tuple


VERSION = "v2026-02-13-core-monitors-bundle-mirror-v1"


@dataclass
class CheckResult:
    subsystem: str
    status: str  # ok | warn | fail
    notes: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_mtime_utc_iso(p: Path) -> str:
    dt = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def age_seconds(p: Path, now_ts: float) -> float:
    return max(0.0, now_ts - p.stat().st_mtime)


def fmt_age(age_s: float) -> str:
    # Human-ish compact age format
    if age_s < 90:
        return f"{int(age_s)}s"
    if age_s < 90 * 60:
        return f"{age_s/60:.1f}m"
    if age_s < 72 * 3600:
        return f"{age_s/3600:.1f}h"
    return f"{age_s/86400:.1f}d"


def ok_if_recent_file(
    subsystem: str,
    path: Path,
    *,
    max_age_s: float,
    now_ts: float,
    missing_is: str = "fail",
    label: str | None = None,
) -> CheckResult:
    """
    Returns ok if file exists and mtime <= max_age_s, warn if older, fail if missing.
    """
    disp = label or str(path)
    if not path.exists():
        status = "fail" if missing_is == "fail" else "warn"
        return CheckResult(subsystem, status, f"missing: {disp}")
    try:
        a = age_seconds(path, now_ts)
    except Exception as e:
        return CheckResult(subsystem, "warn", f"stat failed for {disp}: {e}")

    if a <= max_age_s:
        return CheckResult(subsystem, "ok", "ran clean")
    return CheckResult(subsystem, "warn", f"stale ({fmt_age(a)} old): {disp}")


def ok_if_recent_any(
    subsystem: str,
    candidates: List[Path],
    *,
    max_age_s: float,
    now_ts: float,
) -> CheckResult:
    """
    Returns ok if ANY candidate exists and is recent.
    Warn if exists but stale.
    Fail if none exist.
    """
    existing: List[Tuple[Path, float]] = []
    for p in candidates:
        if p.exists():
            try:
                existing.append((p, age_seconds(p, now_ts)))
            except Exception:
                # ignore stat errors here; will be caught below
                pass

    if not existing:
        return CheckResult(subsystem, "fail", "missing: no expected files found")

    # choose newest
    existing.sort(key=lambda t: t[1])
    p, a = existing[0]
    if a <= max_age_s:
        return CheckResult(subsystem, "ok", "ran clean")
    return CheckResult(subsystem, "warn", f"stale ({fmt_age(a)} old): {p}")


def write_snapshot(snapshot_path: Path, lines: List[str], *, dry_run: bool) -> None:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines).rstrip() + "\n"
    if dry_run:
        print(content)
        return
    snapshot_path.write_text(content, encoding="utf-8")


def mirror_snapshot(snapshot_path: Path, repo_root: Path, *, dry_run: bool) -> None:
    """
    Mirror canonical snapshot into repo tree for GitHub visibility.
    Non-fatal on error.
    """
    mirror = repo_root / "memory/logs/status/system_health_snapshot.md"
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return
    mirror.write_text(snapshot_path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print output only; do not write files")
    ap.add_argument(
        "--max-age-hours",
        type=float,
        default=float(os.environ.get("CORE_MON_MAX_AGE_HOURS", "48")),
        help="freshness window in hours for log/heartbeat checks (default 48)",
    )
    ap.add_argument(
        "--mem-root",
        default=os.environ.get("MEM_ROOT", "/home/rafa1215/memory"),
        help="canonical memory root (default /home/rafa1215/memory)",
    )
    args = ap.parse_args()

    dry_run: bool = args.dry_run
    mem_root = Path(args.mem_root).resolve()
    repo_root = Path(__file__).resolve().parents[1]  # /home/rafa1215/consensus-project
    status_dir = mem_root / "logs/status"
    system_dir = mem_root / "logs/system"
    now_ts = datetime.now(timezone.utc).timestamp()
    max_age_s = float(args.max_age_hours) * 3600.0

    # Canonical output
    snapshot_path = status_dir / "system_health_snapshot.md"

    # Checks (simple + robust; based on file existence/freshness)
    # Note: These are intentionally conservative and file-based.
    checks: List[CheckResult] = []

    # Absorption: prefer explicit absorption status file, else any absorb log
    checks.append(
        ok_if_recent_any(
            "absorb_runner",
            [
                status_dir / "absorption_status.md",
                system_dir / "absorb_public_marker_ok.log",
                system_dir / "absorb_runner_ok.log",
                system_dir / "absorb_runner.log",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    checks.append(
        ok_if_recent_file(
            "absorb_status_report",
            status_dir / "absorption_status.md",
            max_age_s=max_age_s,
            now_ts=now_ts,
            missing_is="warn",
            label="absorption_status.md",
        )
    )

    # Geofence heartbeat
    checks.append(
        ok_if_recent_any(
            "geofence_heartbeat",
            [
                system_dir / "heartbeat.md",
                system_dir / "geofence_heartbeat.log",
                system_dir / "geofence_heartbeat.md",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    # Gmail refresh guard
    checks.append(
        ok_if_recent_any(
            "gmail_refresh_guard_v3",
            [
                system_dir / "gmail_status.md",
                system_dir / "gmail_refresh_guard.log",
                system_dir / "gmail_refresh_guard_v3.log",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    # Status report generator (weekly status report file present)
    checks.append(
        ok_if_recent_any(
            "generate_status_report",
            [
                status_dir / "weekly_status_report.md",
                system_dir / "status_report_{}.md".format(datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                system_dir / "status_report_latest.md",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    # Movies monitor
    checks.append(
        ok_if_recent_any(
            "movies_monitor",
            [
                system_dir / "movies_monitor_status.json",
                status_dir / "movie_list_status.md",
                system_dir / "movies_monitor.log",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    # Agents orchestrator / MCL logs indicate system running
    checks.append(
        ok_if_recent_any(
            "agents_orchestrator",
            [
                system_dir / "master_control_loop.log",
                system_dir / "agent_self_repair.log",
                system_dir / "agent_evolution_cycle.log",
            ],
            max_age_s=max_age_s,
            now_ts=now_ts,
        )
    )

    # Build snapshot content
    gen_ts = utc_now_iso()
    lines: List[str] = []
    lines.append("# System Health Snapshot")
    lines.append(f"- Generated: {gen_ts}")
    lines.append(f"- Dry run: {str(dry_run).lower()}")
    lines.append(f"- Agent: core_monitors_bundle.py {VERSION}")
    lines.append(f"- mem_root: {mem_root}")
    lines.append("")
    lines.append("| Subsystem | Status | Notes |")
    lines.append("|---|---|---|")

    # Normalize statuses, and include stable notes for "ok" rows
    for r in checks:
        s = r.status.strip().lower()
        if s not in ("ok", "warn", "fail"):
            s = "warn"
        lines.append(f"| {r.subsystem} | {s} | {r.notes} |")

    # Summarize
    any_fail = any(r.status == "fail" for r in checks)
    any_warn = any(r.status == "warn" for r in checks)
    lines.append("")
    overall = "ok"
    if any_fail:
        overall = "fail"
    elif any_warn:
        overall = "warn"
    lines.append(f"- Overall: {overall}")

    # Write canonical + mirror
    write_snapshot(snapshot_path, lines, dry_run=dry_run)
    try:
        mirror_snapshot(snapshot_path, repo_root, dry_run=dry_run)
    except Exception as e:
        # Non-fatal: canonical snapshot already written
        print(f"[WARN] mirror snapshot failed: {e}", file=sys.stderr)

    return 1 if any_fail and not dry_run else 0


if __name__ == "__main__":
    raise SystemExit(main())
