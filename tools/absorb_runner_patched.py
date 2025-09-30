#!/usr/bin/env python3
import subprocess, sys, datetime, pathlib

LOG_FULL = pathlib.Path("memory/logs/heartbeat/full_memory_absorption.log")
LOG_HEARTBEAT = pathlib.Path("memory/logs/heartbeat/memory_absorption_heartbeat.log")

def log(msg):
    stamp = datetime.datetime.utcnow().strftime("[%Y-%m-%dT%H:%M:%SZ]")
    with LOG_FULL.open("a") as f:
        f.write(f"{stamp} {msg}\n")

def main():
    log("Starting absorb run")
    try:
        cmd = ["python3", "tools/absorb_memory.py", "--full", "--verbose"]
        with LOG_HEARTBEAT.open("a") as f:
            subprocess.run(cmd, stdout=f, stderr=f, check=False)
        log("Finished absorb run")
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
