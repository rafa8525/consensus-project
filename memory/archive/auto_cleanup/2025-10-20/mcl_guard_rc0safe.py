#!/usr/bin/env python3
import os, sys, time, subprocess
from pathlib import Path

BASE = Path(os.environ.get("PROJECT_DIR", str(Path.home() / "consensus-project")))
LOG_DIR = BASE / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOG_DIR / "mcl_guard.log"
OUT = LOG_DIR / "mcl_child.out"
ERR = LOG_DIR / "mcl_child.err"

MCL_ENTRY = os.environ.get("MCL_ENTRY", str(BASE / "mcl_v2" / "main.py"))
MAX_RESTARTS = 12
BACKOFF = 5

def log(msg: str):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}\n"
    with LOG.open("a", encoding="utf-8") as f: f.write(line)
    print(line, end="")

def main():
    restarts = 0
    while True:
        log(f"spawn cmd: python3.10 {MCL_ENTRY}")
        out = OUT.open("ab", buffering=0)
        err = ERR.open("ab", buffering=0)
        child = subprocess.Popen(
            ["python3.10", MCL_ENTRY],
            cwd=str(BASE),
            stdout=out, stderr=err, env=os.environ.copy()
        )
        log(f"spawned loop pid={child.pid}")
        rc = child.wait()
        log(f"loop exited rc={rc}")

        # >>> KEY POLICY: do NOT respawn on a clean exit
        if rc == 0:
            log("child exited 0 — not respawning")
            break

        restarts += 1
        if restarts >= MAX_RESTARTS:
            log("max restarts reached; stopping")
            break
        time.sleep(BACKOFF)

if __name__ == "__main__":
    sys.exit(main())
