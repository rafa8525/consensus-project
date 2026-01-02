#!/usr/bin/env python3
"""
tools/absorb_hourly.py

Runs hourly. Decides whether to run an AM or PM absorption window based on local time.
- Safe: does not send SMS.
- Concurrency-safe: lock file prevents overlapping runs.
- Idempotent per-day per-window: writes a JSONL log; won't rerun a window once it succeeded today
  unless --force is used.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, date, time as dtime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  # py3.9+
except Exception:
    ZoneInfo = None  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "absorb"
JSONL_PATH = LOG_DIR / "absorb_hourly.jsonl"
TEXT_LOG_PATH = LOG_DIR / "absorb_hourly.log"
LOCK_DIR = PROJECT_ROOT / "memory" / "locks"
LOCK_PATH = LOCK_DIR / "absorb_hourly.lock"

DEFAULT_TZ = os.getenv("ABSORB_TZ", "America/Los_Angeles")

AM_START = dtime(4, 0)
AM_END   = dtime(11, 59)
PM_START = dtime(15, 0)
PM_END   = dtime(22, 59)

PA_MAX_RETRIES = 4
DEFAULT_LOCAL_RETRIES = 2

def pick_absorb_cmd() -> list[str]:
    override = os.getenv("ABSORB_CMD", "").strip()
    if override:
        return shlex.split(override)

    cand1 = PROJECT_ROOT / "tools" / "absorb_memory.py"
    if cand1.exists():
        return [sys.executable, str(cand1), "--full"]

    cand2 = PROJECT_ROOT / "tools" / "run_absorption.py"
    if cand2.exists():
        return [sys.executable, str(cand2)]

    cand3 = PROJECT_ROOT / "tools" / "absorb_runner.py"
    if cand3.exists():
        return [sys.executable, str(cand3)]

    raise FileNotFoundError("No absorption entrypoint found (absorb_memory.py/run_absorption.py/absorb_runner.py).")

def now_local() -> datetime:
    if ZoneInfo is None:
        return datetime.now()
    return datetime.now(ZoneInfo(DEFAULT_TZ))

def iso(ts: datetime) -> str:
    return ts.isoformat()

def ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOCK_DIR.mkdir(parents=True, exist_ok=True)

def append_text(line: str) -> None:
    ensure_dirs()
    with open(TEXT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")

def append_jsonl(obj: dict) -> None:
    ensure_dirs()
    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")

def load_recent_entries(max_lines: int = 2000) -> list[dict]:
    if not JSONL_PATH.exists():
        return []
    with open(JSONL_PATH, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        read_back = min(size, 512 * 1024)
        f.seek(size - read_back, os.SEEK_SET)
        chunk = f.read().decode("utf-8", errors="ignore")
    lines = [ln for ln in chunk.splitlines() if ln.strip()]
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    out: list[dict] = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out

def day_has_success(entries: list[dict], day: date, window: str) -> bool:
    d = day.isoformat()
    for e in reversed(entries):
        if e.get("day") == d and e.get("window") == window and e.get("status") == "success":
            return True
    return False

def between(t: dtime, start: dtime, end: dtime) -> bool:
    return start <= t <= end

def detect_pythonanywhere() -> bool:
    return bool(os.getenv("PYTHONANYWHERE_SITE") or os.getenv("PYTHONANYWHERE_DOMAIN") or os.getenv("PA_USERNAME"))

@dataclass
class Lock:
    path: Path
    fd: int | None = None

    def acquire(self) -> None:
        ensure_dirs()
        self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        payload = f"pid={os.getpid()} ts={iso(now_local())}\n"
        os.write(self.fd, payload.encode("utf-8"))

    def release(self) -> None:
        try:
            if self.fd is not None:
                os.close(self.fd)
        except Exception:
            pass
        try:
            if self.path.exists():
                self.path.unlink()
        except Exception:
            pass

def run_absorb(window: str, mode: str, dry_run: bool = False) -> bool:
    cmd = pick_absorb_cmd()
    ts0 = now_local()
    start = time.time()

    append_text(f"[absorb_hourly] {iso(ts0)} window={window} mode={mode}")
    append_jsonl({"ts": iso(ts0), "day": ts0.date().isoformat(), "window": window, "mode": mode, "event": "start"})

    if dry_run:
        append_text(f"[absorb_hourly] DRY_RUN cmd={' '.join(cmd)}")
        append_jsonl({"ts": iso(now_local()), "day": ts0.date().isoformat(), "window": window, "mode": mode,
                      "event": "finish", "status": "success", "dry_run": True, "rc": 0, "duration_s": 0})
        return True

    try:
        p = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=int(os.getenv("ABSORB_TIMEOUT_S", "1800")),
        )
        dur = round(time.time() - start, 3)
        out = (p.stdout or "").strip()
        tail = "\n".join(out.splitlines()[-40:]) if out else ""
        append_text(f"[absorb_hourly] rc={p.returncode} duration_s={dur}")
        if tail:
            append_text("[absorb_hourly] output_tail:\n" + tail)
        ok = (p.returncode == 0)
        append_jsonl({
            "ts": iso(now_local()),
            "day": ts0.date().isoformat(),
            "window": window,
            "mode": mode,
            "event": "finish",
            "status": "success" if ok else "error",
            "rc": p.returncode,
            "duration_s": dur,
            "output_tail": tail,
        })
        return ok
    except subprocess.TimeoutExpired:
        dur = round(time.time() - start, 3)
        append_text(f"[absorb_hourly] TIMEOUT after {dur}s")
        append_jsonl({
            "ts": iso(now_local()),
            "day": ts0.date().isoformat(),
            "window": window,
            "mode": mode,
            "event": "finish",
            "status": "error",
            "rc": -1,
            "duration_s": dur,
            "output_tail": "TIMEOUT",
        })
        return False
    except Exception as e:
        dur = round(time.time() - start, 3)
        append_text(f"[absorb_hourly] EXCEPTION after {dur}s: {type(e).__name__}: {e}")
        append_jsonl({
            "ts": iso(now_local()),
            "day": ts0.date().isoformat(),
            "window": window,
            "mode": mode,
            "event": "finish",
            "status": "error",
            "rc": -2,
            "duration_s": dur,
            "output_tail": f"{type(e).__name__}: {e}",
        })
        return False

def run_with_retry(window: str, mode: str, dry_run: bool, max_retries: int | None) -> bool:
    if max_retries is None:
        max_retries = PA_MAX_RETRIES if detect_pythonanywhere() else DEFAULT_LOCAL_RETRIES

    for attempt in range(max_retries + 1):
        ok = run_absorb(window, mode, dry_run=dry_run)
        if ok:
            return True
        if attempt < max_retries:
            wait_s = min((attempt + 1) * 10, 30)
            append_text(f"[absorb_hourly] retrying in {wait_s}s (attempt {attempt+2}/{max_retries+1})")
            time.sleep(wait_s)
    return False

def decide_window(entries: list[dict], now: datetime) -> tuple[str | None, str]:
    today = now.date()
    t = now.time()

    am_done = day_has_success(entries, today, "am")
    pm_done = day_has_success(entries, today, "pm")

    if not am_done and between(t, AM_START, AM_END):
        return ("am", "scheduled")
    if not pm_done and between(t, PM_START, PM_END):
        return ("pm", "scheduled")

    if not pm_done and t > PM_END:
        return ("pm", "catchup")
    if not am_done and t > AM_END:
        return ("am", "catchup")

    return (None, "none")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", choices=["am", "pm"])
    ap.add_argument("--mode", default=None, choices=["scheduled", "catchup", "manual"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-retries", type=int, default=None)
    args = ap.parse_args()

    ensure_dirs()
    lock = Lock(LOCK_PATH)

    try:
        lock.acquire()
    except FileExistsError:
        append_text(f"[absorb_hourly] {iso(now_local())} lock exists; exiting")
        return 0

    try:
        entries = load_recent_entries()
        now = now_local()

        if args.force:
            window = args.force
            mode = args.mode or "manual"
            ok = run_with_retry(window, mode, args.dry_run, args.max_retries)
            return 0 if ok else 1

        window, mode = decide_window(entries, now)
        if window is None:
            append_text(f"[absorb_hourly] {iso(now)} nothing due right now")
            return 0

        if args.mode:
            mode = args.mode

        ok = run_with_retry(window, mode, args.dry_run, args.max_retries)
        return 0 if ok else 1

    finally:
        lock.release()

if __name__ == "__main__":
    raise SystemExit(main())
