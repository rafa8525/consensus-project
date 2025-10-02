#!/usr/bin/env python3
import subprocess
import os

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)

if __name__ == "__main__":
    # Knowledge graph update
    run("knowledge_graph.py")

    # Symbolic reasoning engine
    run("symbolic_reasoning.py")

    print("✅ Knowledge + Symbolic Reasoning combined run complete.")
