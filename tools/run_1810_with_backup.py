#!/usr/bin/env python3
"""18:10 UTC combined scheduled task: original jobs plus verified Drive backup.

Deliberately opt-in. --check performs no network or job execution.
No secret values, stdout, or stderr from child processes are logged.
"""
from __future__ import annotations
import argparse
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path.home() / ".secrets/google"
SUCCESS = PRIVATE / "acs_backup_success.json"
LOCK = PRIVATE / "acs_1810_scheduler.lock"
STEPS = (
    ("movie_export", ("tools/movie_export_from_sheets.py",), 1200),
    ("absorption", ("tools/absorb_runner.py",), 1800),
    ("public_marker", ("tools/write_absorption_public_marker.py",), 300),
)
BACKUP = ("tools/run_acs_backup_cycle.py", "--run")


def already_verified_today(receipt: Path, now: datetime) -> bool:
    try:
        r = json.loads(receipt.read_text(encoding="utf-8"))
        stamp = datetime.fromisoformat(r["finished_at_utc"].replace("Z", "+00:00"))
        return (
            r.get("status") == "uploaded_verified"
            and r.get("restore_verified") is True
            and type(r.get("file_count")) is int and r["file_count"] > 0
            and isinstance(r.get("remote_id"), str) and bool(r["remote_id"])
            and len(r.get("encrypted_sha256", "")) == 64
            and stamp.tzinfo is not None
            and -900 <= (now - stamp).total_seconds()
            and stamp.astimezone(timezone.utc).date() == now.date()
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False


def run_step(name: str, args: tuple[str, ...], timeout: int) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, *args], cwd=ROOT, timeout=timeout,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False,
        )
        ok = result.returncode == 0
        print(json.dumps({"step": name, "ok": ok, "exit_code": result.returncode}), flush=True)
        return ok
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"step": name, "ok": False, "error_type": type(exc).__name__}), flush=True)
        return False


def run_all() -> int:
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(LOCK, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"status": "already_running", "ok": False}))
            return 1
        results = []
        for name, args, timeout in STEPS:
            results.append(run_step(name, args, timeout))
        if already_verified_today(SUCCESS, datetime.now(timezone.utc)):
            backup_ok = True
            print(json.dumps({"step": "encrypted_backup", "ok": True, "status": "verified_today_skip"}))
        else:
            backup_ok = run_step("encrypted_backup", BACKUP, 1800)
            if backup_ok and not already_verified_today(SUCCESS, datetime.now(timezone.utc)):
                backup_ok = False
                print(json.dumps({"step": "backup_receipt", "ok": False, "status": "missing_or_unverified"}))
        all_ok = all(results) and backup_ok
        print(json.dumps({"status": "ok" if all_ok else "degraded",
                          "backup_ok": backup_ok, "other_jobs_ok": all(results)}))
        return 0 if all_ok else 1
    finally:
        os.close(lock)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check and not args.run:
        print(json.dumps({"status": "checked", "steps": [x[0] for x in STEPS],
                          "backup": BACKUP[0], "no_jobs_run": True}))
        return 0
    if not args.run:
        parser.error("use --check or --run")
    return run_all()


if __name__ == "__main__":
    raise SystemExit(main())
