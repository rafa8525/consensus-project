#!/usr/bin/env python3
import subprocess
import os

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

if __name__ == "__main__":
# Mutation_68b1ff
    # Fitness data integration
    run("fitness_integration.py")

    # Daily progress evaluation
    run("progress_evaluator.py")

    print("✅ Fitness + Progress combined run complete.")