#!/usr/bin/env python3
import subprocess
import os

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

if __name__ == "__main__":
    # System watchdog
    run("mcl_guard.py")

    # Security audit (skips unless 1st of month)
    run("security_audit.py")

    print("✅ System Guard Master run complete (Guard + Security).")
