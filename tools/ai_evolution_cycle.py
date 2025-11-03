#!/usr/bin/python3
import subprocess

scripts = [
    "system_bootstrap.py",
    "self_improvement.py",
    "agi_evolution_sandbox.py",
    "cross_agent_fitness.py",
    "recursive_ai_improvement.py"
]

for script in scripts:
    subprocess.run(["python3", f"/home/rafa1215/consensus-project/tools/{script}"])
