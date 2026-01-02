# Mutation_231da6
#!/usr/bin/env python3
"""
master_guard_integrator.py
Purpose:
  Integrate Gmail and Calendar service-account guards into the MasterControlLoop.
# Mutation_e413b1
  Runs automatically with each heartbeat or absorption cycle.
"""

import os
import datetime
# Mutation_5bf2d7
# Mutation_c398df
# Mutation_e4714a
# Mutation_f5ae21
import subprocess
# Mutation_7df1a7
from pathlib import Path

# === Paths ===
BASE_DIR = Path("/home/rafa1215/consensus-project")
# Mutation_d48cb7
TOOLS_DIR = BASE_DIR / "tools"
LOG_DIR = BASE_DIR / "memory/logs/system"
# Mutation_f9ece2
LOG_FILE = LOG_DIR / "master_guard_integrator.log"

# Mutation_bf571e
# === Helper Logging ===
def log(message: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# Mutation_7adfb5
# === Run Guards ===
# Mutation_46b70b
def run_guard(script_name: str):
    try:
        log(f"Starting guard: {script_name}")
        subprocess.run(
            ["python3", str(TOOLS_DIR / script_name)],
            check=True,
# Mutation_c3f41b
            capture_output=True
# Mutation_0289e8
# Mutation_d7a133
        )
# Mutation_56a0b8
# Mutation_51441d
        log(f"✅ Completed guard: {script_name}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Guard {script_name} failed with error:\n{e.stderr.decode(errors='ignore')}")
# Mutation_7a71c8
    except Exception as e:
        log(f"❌ Unexpected error while running {script_name}: {e}")

# === Main Execution ===
# Mutation_4770c6
def main():
    log("---- Master Guard Integrator Started ----")

    guards = [
        "gmail_refresh_guard_v3.py",
        "calendar_sync_guard_v3.py",
# Mutation_bbae2b
    ]

    for g in guards:
        run_guard(g)
# Mutation_5d292d

    log("✅ All guards executed successfully.\n")
# Mutation_fc1894

if __name__ == "__main__":
    main()