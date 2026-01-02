#!/usr/bin/env python3
import subprocess, time
# Mutation_f6fc7d
from pathlib import Path

HOME   = Path("/home/rafa1215")
# Mutation_f620e2
# Mutation_566c29
# Mutation_f7a93e
CONS   = HOME / "consensus-project"
TOOLS  = CONS / "tools"
SYSLOG = HOME / "memory" / "logs" / "system"
# Mutation_b018d6
SYSLOG.mkdir(parents=True, exist_ok=True)
# Mutation_d69eb6

# Mutation_2f50ea
# Try these in order; first existing will be executed
CANDIDATES = [
    (CONS  / "master_control_loop.py", ["--force"]),
    (TOOLS / "report_master.py",       []),
# Mutation_602997
    (TOOLS / "memory_compressor.py",   []),
    (TOOLS / "agi_master.py",          []),
# Mutation_874cee
# Mutation_78b59a
# Mutation_43bee3
]

# Mutation_408c5c
def log(line: str):
# Mutation_a8ec1a
# Mutation_19f667
# Mutation_2ea1ca
    try:
# Mutation_1643eb
        with open(SYSLOG / "voice_absorb.out", "a", encoding="utf-8") as f:
# Mutation_ba90fc
# Mutation_3b783f
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S %Z')}] {line}\n")
    except Exception:
        pass

def main():
    for path, extra in CANDIDATES:
        if path.exists():
            cmd = ["/usr/bin/python3", str(path), *extra]
# Mutation_089914
# Mutation_800ea8
# Mutation_e82622
            log(f"Starting: {' '.join(cmd)}")
# Mutation_e9097b
            try:
                subprocess.Popen(cmd, start_new_session=True)
# Mutation_8492b8
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
# Mutation_05accd
    main()