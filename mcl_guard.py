#!/usr/bin/env python3
# mcl_guard.py
# Purpose: Robust, idempotent guard that runs the memory "absorb" task with auto-retry,
#          exponential backoff with jitter, lockfile protection, and structured logging.
# Platform: PythonAnywhere-safe. No emojis. No console closing side effects.

import os
import sys
import json
import time
import random
import shutil
import subprocess
import datetime
import traceback
from pathlib import Path

# ====== CONFIG ======
PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
HEARTBEAT_DIR = PROJECT_ROOT / "memory" / "logs" / "heartbeat"
STATUS_JSON = PROJECT_ROOT / "memory" / "logs" / "system" / "absorb_status.json"
MD_LOG = PROJECT_ROOT / "memory" / "logs" / "system" / "absorb_guard.md"
LOCKFILE = PROJECT_ROOT / "memory" / "locks" / "absorb_guard.lock"
MIN_FREE_MB = 300  # fail fast if free space below this
MAX_RETRIES = 8
BASE_BACKOFF_SEC = 10
BACKOFF_CAP_SEC = 300  # max backoff cap
GIT_BIN = "/usr/bin/git"

# Command to run the actual absorption. Adjust if your absorb script differs.
# Option A (preferred if present):
ABSORB_CMD = ["python3", "tools/absorb_memory.py", "--full-scan"]
# Option B (fallbacks — uncomment if you use one of these instead):
# ABSORB_CMD = ["python3", "absorb_runner.py"]
# ABSORB_CMD = ["python3", "tools/absorb_status_report.py", "--run-and-write"]

# ====== UTILS ======
def now_utc_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def ensure_dirs():
    for d in [LOG_DIR, HEARTBEAT_DIR, LOCKFILE.parent]:
        d.mkdir(parents=True, exist_ok=True)

def log_md(line: str):
    ensure_dirs()
    ts = now_utc_iso()
    with MD_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def write_status(status: dict):
    ensure_dirs()
    # merge with previous to preserve history fields if any
    prev = {}
    if STATUS_JSON.exists():
        try:
            prev = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
    prev.update(status)
    STATUS_JSON.write_text(json.dumps(prev, indent=2), encoding="utf-8")

def heartbeat(note: str):
    ensure_dirs()
    date = datetime.date.today().isoformat()
    hb_path = HEARTBEAT_DIR / f"absorb_guard_{date}.md"
    ts = now_utc_iso()
    with hb_path.open("a", encoding="utf-8") as f:
        f.write(f"- {ts} {note}\n")

def have_enough_disk_space(path="/home"):
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)
        return free_mb >= MIN_FREE_MB, free_mb
    except Exception:
        return True, -1

def run(cmd, cwd=None, env=None, timeout=None):
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )

def with_lock(lockfile: Path):
    # very simple pid lock
    if lockfile.exists():
        try:
            data = json.loads(lockfile.read_text(encoding="utf-8"))
            pid = data.get("pid")
            ts = data.get("time")
        except Exception:
            pid, ts = None, None
        # If stale lock (process no longer exists), clear it
        if pid and not os.path.exists(f"/proc/{pid}"):
            try:
                lockfile.unlink(missing_ok=True)
            except Exception:
                pass
        else:
            return False
    # create lock
    try:
        lockfile.write_text(json.dumps({"pid": os.getpid(), "time": now_utc_iso()}), encoding="utf-8")
        return True
    except Exception:
        return False

def release_lock(lockfile: Path):
    try:
        lockfile.unlink(missing_ok=True)
    except Exception:
        pass

def git_safe_pull():
    # optional: keep local working copy up-to-date before absorb
    if not shutil.which(GIT_BIN):
        return True, "git not found; skipping"
    cmds = [
        [GIT_BIN, "status", "--porcelain"],
        [GIT_BIN, "pull", "--rebase", "--autostash"],
    ]
    for cmd in cmds:
        p = run(cmd, cwd=PROJECT_ROOT)
        if p.returncode != 0:
            return False, f"cmd={' '.join(cmd)} rc={p.returncode} err={p.stderr.strip()}"
    return True, "git pull ok"

# ====== MAIN LOGIC ======
def main():
    ensure_dirs()
    ts = now_utc_iso()
    log_md("mcl_guard start")
    heartbeat("start")

    # Disk space check
    ok_space, free_mb = have_enough_disk_space("/")
    if not ok_space:
        msg = f"Insufficient disk space: {free_mb} MB free; need >= {MIN_FREE_MB} MB"
        log_md(msg)
        write_status({
            "last_run": ts,
            "last_result": "failure",
            "last_error": msg,
            "free_mb": free_mb
        })
        heartbeat("fail: low disk space")
        return 2

    # Optional: keep repository synced
    ok_pull, pull_msg = git_safe_pull()
    if not ok_pull:
        log_md(f"git sync warning: {pull_msg}")

    # Concurrency guard
    if not with_lock(LOCKFILE):
        msg = "Another absorb_guard instance appears to be running; exiting."
        log_md(msg)
        write_status({
            "last_run": ts,
            "last_result": "skipped",
            "reason": "lock",
        })
        heartbeat("skipped: lock")
        return 0

    try:
        attempt = 0
        last_err = ""
        while attempt <= MAX_RETRIES:
            attempt += 1
            start = time.time()
            log_md(f"attempt {attempt} running: {' '.join(ABSORB_CMD)}")
            p = run(ABSORB_CMD, cwd=PROJECT_ROOT, timeout=60*25)  # 25m hard timeout
            dur = round(time.time() - start, 2)

            if p.returncode == 0:
                # success
                log_md(f"attempt {attempt} success in {dur}s")
                write_status({
                    "last_run": ts,
                    "last_result": "success",
                    "last_success_time": now_utc_iso(),
                    "duration_sec": dur,
                    "stdout_tail": p.stdout[-800:].strip() if p.stdout else "",
                })
                heartbeat("success")
                return 0

            # failure path
            last_err = f"rc={p.returncode} stdout_tail={p.stdout[-400:].strip() if p.stdout else ''} stderr_tail={p.stderr[-400:].strip() if p.stderr else ''}"
            log_md(f"attempt {attempt} failed in {dur}s: {last_err}")

            if attempt > MAX_RETRIES:
                break

            # backoff with jitter
            backoff = min(BACKOFF_CAP_SEC, BASE_BACKOFF_SEC * (2 ** (attempt - 1)))
            backoff = int(backoff * (0.8 + 0.4 * random.random()))
            heartbeat(f"retrying in {backoff}s")
            time.sleep(backoff)

        # if we exit loop without success:
        log_md("all retries exhausted; giving up for this run")
        write_status({
            "last_run": ts,
            "last_result": "failure",
            "last_error": last_err,
            "retries": MAX_RETRIES
        })
        heartbeat("failure after retries")
        return 1

    except Exception as e:
        err = f"guard exception: {repr(e)}\n{traceback.format_exc()}"
        log_md(err)
        write_status({
            "last_run": ts,
            "last_result": "failure",
            "last_error": err
        })
        heartbeat("exception")
        return 3

    finally:
        release_lock(LOCKFILE)
        log_md("mcl_guard end")

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
