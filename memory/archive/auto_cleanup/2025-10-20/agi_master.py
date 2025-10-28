#!/usr/bin/env python3
import subprocess
import os

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

if __name__ == "__main__":
    # AGI simulation run
    run("agi_simulation.py")

    # Evolutionary AGI loop
    run("evolutionary_agi.py")

    print("✅ AGI Master run complete (Simulation + Evolution).")
