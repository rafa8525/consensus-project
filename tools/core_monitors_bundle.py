#!/usr/bin/env python3
"""
tools/core_monitors_bundle.py

Runs a manifest-defined bundle of scripts safely:
- Uses config/core_monitors_manifest.txt as the single source of truth.
- Never floods the console: child stdout/stderr are redirected to per-script log files.
- Writes a simple health snapshot to: /home/rafa1215/memory/logs/status/system_health_snapshot.md
- FAILS FAST with NON-ZERO exit if manifest is missing or contains missing entries (even in --dry-run).
- Enforces per-script timeouts and kills hung processes.

Usage:
  python3 tools/core_monitors_bundle.py --dry-run
  python3 tools/core_monitors_bundle.py

Recommended:
  python3 tools/console_guard.py --timeout 120 --max-bytes 12000 -- \
    python3 tools/core_monitors_bundle.py
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root() -> Path:
    # tools/ -> repo root
    return Path(__file__).resolve().parent.parent


# Rafael canonical status/log locations (outside repo)
STATUS_DIR = Path("/home/rafa1215/memory/logs/status")
EXEC_DIR = Path("/home/rafa1215/memory/logs/system/exec")


def ensure_dirs() -> None:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    EXEC_DIR.mkdir(parents=True, exist_ok=True)


def default_manifest_path() -> Path:
    return project_root() / "config" / "core_monitors_manifest.txt"


def parse_manifest(manifest: Path) -> List[str]:
    """
    Returns a list of relative script paths (as strings) from the manifest.
    Ignores blank lines and comments beginning with '#'.
    """
    lines = manifest.read_text(encoding="utf-8").splitlines()
    items: List[str] = []
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        # Normalize: no leading ./, no absolute paths
        s = s.lstrip("./")
        if s.startswith("/"):
            raise ValueError(f"Manifest contains absolute path (not allowed): {s}")
        items.append(s)
    return items


def discover_candidates(repo: Path, limit: int = 40) -> List[str]:
    """
    Best-effort discovery list for debugging when manifest is missing.
    """
    patterns = ("agent", "monitor", "orchestrator", "absorb", "geofence", "gmail", "status", "prediction", "movie")
    out: List[str] = []
    for p in repo.rglob("*.py"):
        rel = str(p.relative_to(repo))
        low = rel.lower()
        if any(k in low for k in patterns):
            out.append(rel)
    out.sort()
    return out[:limit]


@dataclass
class CheckResult:
    runnable: List[str]
    missing: List[str]


def check_manifest_entries(repo: Path, entries: List[str]) -> CheckResult:
    runnable: List[str] = []
    missing: List[str] = []
    for rel in entries:
        path = repo / rel
        if path.exists() and path.is_file():
            runnable.append(rel)
        else:
            missing.append(rel)
    return CheckResult(runnable=runnable, missing=missing)


def snapshot_path() -> Path:
    return STATUS_DIR / "system_health_snapshot.md"


def write_snapshot(dry_run: bool, rows: List[Tuple[str, str, str]]) -> None:
    """
    rows: (subsystem, status, notes)
    """
    sp = snapshot_path()
    lines: List[str] = []
    lines.append("# System Health Snapshot")
    lines.append(f"- Generated: {utc_iso()}")
    lines.append(f"- Dry run: {str(dry_run).lower()}")
    lines.append("| Subsystem | Status | Notes |")
    lines.append("|---|---|---|")
    for subsystem, status, notes in rows:
        lines.append(f"| {subsystem} | {status} | {notes} |")
    sp.write_text("\n".join(lines) + "\n", encoding="utf-8")


def subsystem_name(rel: str) -> str:
    # tools/foo_bar.py -> foo_bar
    base = Path(rel).name
    return base[:-3] if base.endswith(".py") else base


def kill_process_tree(proc: subprocess.Popen) -> None:
    """
    Kill the process group if possible, else the process.
    """
    try:
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass


def run_script(repo: Path, rel: str, timeout_s: int, run_ts: str) -> Tuple[str, str, str]:
    """
    Returns (subsystem, status, notes)
    status ∈ {ready, ok, fail, timeout}
    """
    name = subsystem_name(rel)
    script_path = repo / rel

    # Per-script log file
    safe_name = name.replace(" ", "_")
    child_log = EXEC_DIR / f"child_{safe_name}_{run_ts}.log"

    if not script_path.exists():
        return (name, "missing", "not found")

    # Redirect child stdout+stderr to file to avoid console flooding
    with child_log.open("ab") as lf:
        lf.write(b"\n" + (b"=" * 80) + b"\n")
        lf.write(f"[{utc_iso()}] START {rel}\n".encode("utf-8"))
        lf.flush()

        try:
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(repo),
                stdout=lf,
                stderr=lf,
                start_new_session=True,  # gives us a process group to kill
                text=False,
            )
        except Exception as exc:
            lf.write(f"[{utc_iso()}] EXCEPTION spawning {rel}: {exc}\n".encode("utf-8"))
            lf.flush()
            return (name, "fail", f"spawn error (see {child_log})")

        try:
            rc = proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            kill_process_tree(proc)
            try:
                proc.wait(timeout=3)
            except Exception:
                pass
            lf.write(f"[{utc_iso()}] TIMEOUT after {timeout_s}s {rel}\n".encode("utf-8"))
            lf.flush()
            return (name, "timeout", f"timed out (see {child_log})")

        lf.write(f"[{utc_iso()}] END rc={rc} {rel}\n".encode("utf-8"))
        lf.flush()

        if rc == 0:
            return (name, "ok", "ran clean")
        return (name, "fail", f"rc={rc} (see {child_log})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(default_manifest_path()))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=int(os.getenv("CORE_BUNDLE_TIMEOUT", "300")),
                    help="Per-script timeout seconds (default 300)")
    args = ap.parse_args()

    ensure_dirs()
    repo = project_root()
    manifest = Path(args.manifest)

    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    bundle_log = EXEC_DIR / f"bundle_{run_ts}.log"

    rows: List[Tuple[str, str, str]] = []

    # Manifest missing => FAIL (non-zero), but still write snapshot + helpful candidates
    if not manifest.exists():
        candidates = discover_candidates(repo, limit=40)
        rows.append(("core_monitors_bundle", "missing", f"manifest missing: {manifest}"))
        for c in candidates:
            rows.append((subsystem_name(c), "candidate", "discovered"))
        write_snapshot(args.dry_run, rows)

        msg = (
            "[core_monitors_bundle] FAIL (expected until wired)\n"
            f"- repo={repo}\n"
            f"- manifest missing: {manifest}\n"
            "- candidates discovered (first 40 shown):\n  "
            + "\n  ".join(candidates)
            + f"\n- snapshot: {snapshot_path()}\n"
            f"- log: {bundle_log}\n"
        )
        bundle_log.write_text(msg, encoding="utf-8")
        print(msg.strip())
        return 2

    # Parse + validate
    try:
        entries = parse_manifest(manifest)
    except Exception as exc:
        rows.append(("core_monitors_bundle", "fail", f"bad manifest: {exc}"))
        write_snapshot(args.dry_run, rows)
        bundle_log.write_text(f"[{utc_iso()}] BAD MANIFEST: {exc}\n", encoding="utf-8")
        print(f"[core_monitors_bundle] FAIL: bad manifest: {exc}")
        return 2

    chk = check_manifest_entries(repo, entries)

    # Build snapshot rows
    for rel in chk.runnable:
        rows.append((subsystem_name(rel), "ready" if args.dry_run else "ready", "wired"))
    for rel in chk.missing:
        rows.append((subsystem_name(rel), "missing", "not found"))

    # If missing entries => FAIL (non-zero) even in dry-run
    if chk.missing:
        write_snapshot(args.dry_run, rows)

        msg = (
            "[core_monitors_bundle] FAIL (expected until manifest is correct)\n"
            f"- repo={repo}\n"
            f"- manifest={manifest}\n"
            f"- found={len(chk.runnable)} missing={len(chk.missing)} dry_run={args.dry_run}\n"
            "- missing:\n  " + "\n  ".join(chk.missing) + "\n"
            f"- snapshot: {snapshot_path()}\n"
            f"- log: {bundle_log}\n"
        )
        bundle_log.write_text(msg, encoding="utf-8")
        print(msg.strip())
        return 2

    # Dry-run success
    if args.dry_run:
        write_snapshot(True, rows)
        msg = (
            "[core_monitors_bundle] DRY RUN\n"
            f"- repo={repo}\n"
            f"- manifest={manifest}\n"
            f"- runnable={len(chk.runnable)}\n"
            f"- snapshot: {snapshot_path()}\n"
        )
        bundle_log.write_text(msg, encoding="utf-8")
        print(msg.strip())
        return 0

    # Real run: execute each script safely
    exec_rows: List[Tuple[str, str, str]] = []
    any_fail = False

    bundle_log.write_text(
        f"[{utc_iso()}] START bundle manifest={manifest}\n"
        f"timeout_per_script={args.timeout}s\n"
        f"runnable={len(chk.runnable)}\n",
        encoding="utf-8",
    )

    for rel in chk.runnable:
        name, status, notes = run_script(repo, rel, timeout_s=args.timeout, run_ts=run_ts)
        exec_rows.append((name, status, notes))
        if status in ("fail", "timeout", "missing"):
            any_fail = True

    write_snapshot(False, exec_rows)

    with bundle_log.open("a", encoding="utf-8") as f:
        f.write(f"[{utc_iso()}] END bundle any_fail={any_fail}\n")
        f.write(f"snapshot={snapshot_path()}\n")

    # Non-zero if any subsystem failed/timed out
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
