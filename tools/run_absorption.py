#!/usr/bin/env python3
import subprocess, time
from pathlib import Path

HOME   = Path("/home/rafa1215")
CONS   = HOME / "consensus-project"
TOOLS  = CONS / "tools"
SYSLOG = HOME / "memory" / "logs" / "system"
SYSLOG.mkdir(parents=True, exist_ok=True)

# Try these in order; first existing will be executed
CANDIDATES = [
    (CONS  / "master_control_loop.py", ["--force"]),
    (TOOLS / "report_master.py",       []),
    (TOOLS / "memory_compressor.py",   []),
    (TOOLS / "agi_master.py",          []),
]

def log(line: str):
    try:
        with open(SYSLOG / "voice_absorb.out", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S %Z')}] {line}\n")
    except Exception:
        pass

def main():
    for path, extra in CANDIDATES:
        if path.exists():
            cmd = ["/usr/bin/python3", str(path), *extra]
            log(f"Starting: {' '.join(cmd)}")
            try:
                subprocess.Popen(cmd, start_new_session=True)
                return
            except Exception as e:
                log(f"Failed to start {path.name}: {e}")
    # Fallback: write a heartbeat so there is at least a refresh signal
    try:
        with open(SYSLOG / "absorption.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S %Z')}] fallback absorption heartbeat\n")
        log("No candidate scripts found; wrote fallback absorption heartbeat.")
    except Exception as e:
        log(f"Fallback absorption logging failed: {e}")

if __name__ == "__main__":
    main()
