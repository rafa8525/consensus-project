#!/usr/bin/python3
import subprocess

scripts = [
    "security_audit.py",
    "final_validation_report.py",
    "permanent_layer_verifier.py",
    "unified_privacy_guard.py"
]

for script in scripts:
    subprocess.run(["python3", f"/home/rafa1215/consensus-project/tools/{script}"])
