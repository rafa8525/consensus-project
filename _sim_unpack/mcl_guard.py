#!/usr/bin/env python3
import os, time, subprocess, signal, sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(os.environ.get("PROJECT_DIR") or (Path.home() / "consensus-project"))
HB = PROJECT_DIR / "memory/logs/heartbeat/last_heartbeat.txt"
LOGDIR = PROJECT_DIR / "memory/logs/system"
LOGDIR.mkdir(parents=True, exist_ok=True)
LOG = LOGDIR / "mcl_guard.log"
RUNLOG = LOGDIR / "mcl_run.out"
MCL_ENTRY = os.environ.get("MCL_ENTRY", "master_control_loop.py")
PIDFILE = LOGDIR / "mcl_guard.pid"

# Stall/health thresholds (env-overridable)
MAX_STALL = int(
    os.environ.get("MCL_MAX_STALL_SEC", "120")
)  # restart if heartbeat older than this
CHECK_EVERY = int(os.environ.get("MCL_CHECK_SEC", "10"))  # guard loop tick
GRACE_START = int(os.environ.get("MCL_GRACE_START_SEC", "60"))  # grace after spawn
MAX_RESTARTS = int(os.environ.get("MCL_MAX_RESTARTS", "12"))  # limit per session
COOLDOWN = int(os.environ.get("MCL_RESTART_COOLDOWN_SEC", "10"))


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def already_running():
    try:
        if PIDFILE.exists():
            pid = int(PIDFILE.read_text().strip())
            os.kill(pid, 0)
            return True
    except Exception:
        pass
    return False


def write_pid():
    PIDFILE.write_text(str(os.getpid()))


def spawn_child():
    runfh = RUNLOG.open("a")
    p = subprocess.Popen(
        ["python3.10", MCL_ENTRY],
        cwd=str(PROJECT_DIR),
        stdout=runfh,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )
    return p, runfh


def killpg(p, sig):
    try:
        os.killpg(os.getpgid(p.pid), sig)
    except Exception:
        pass


def hb_age_sec():
    try:
        return time.time() - HB.stat().st_mtime
    except FileNotFoundError:
        return 1e9


def main():
    if already_running():
        print("mcl_guard already running; exiting.")
        return 0
    write_pid()
    restarts = 0
    while True:
        p, runfh = spawn_child()
        log(f"spawned loop pid={p.pid}")
        start = time.time()
        while True:
            time.sleep(CHECK_EVERY)
            # child finished?
            rc = p.poll()
            if rc is not None:
                log(f"loop exited rc={rc}")
                try:
                    runfh.close()
                except Exception:
                    pass
                time.sleep(COOLDOWN)
                restarts += 1
                if restarts > MAX_RESTARTS:
                    log("max restarts reached; stopping")
                    return 1
                break  # respawn
            # stall check (after grace)
            if time.time() - start < GRACE_START:
                continue
            age = hb_age_sec()
            if age > MAX_STALL:
                log(f"heartbeat stall ({int(age)}s > {MAX_STALL}s); restarting")
                killpg(p, signal.SIGTERM)
                time.sleep(5)
                killpg(p, signal.SIGKILL)
                try:
                    runfh.close()
                except Exception:
                    pass
                time.sleep(COOLDOWN)
                restarts += 1
                if restarts > MAX_RESTARTS:
                    log("max restarts reached after stall; stopping")
                    return 1
                break  # respawn


if __name__ == "__main__":
    sys.exit(main())
