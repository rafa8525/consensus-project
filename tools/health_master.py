#!/usr/bin/env python3
import subprocess
import os

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

if __name__ == "__main__":
    # Fitness + Progress (already combined earlier)
    run("fitness_progress_master.py")

    # Nutrition pipeline
    run("nutrition_pipeline.py")

    print("✅ Health Master run complete (Fitness + Nutrition).")
