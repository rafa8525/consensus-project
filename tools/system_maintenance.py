#!/usr/bin/python3
import subprocess

scripts = [
    "overnight_guard.py",
    "agent_sweep.py",
    "log_rotate.py",
    "log_memory_manifest.py",
    "integration_manifest.py"
]

for script in scripts:
    subprocess.run(["python3", f"/home/rafa1215/consensus-project/tools/{script}"])
