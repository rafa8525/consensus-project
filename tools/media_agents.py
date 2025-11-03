#!/usr/bin/python3
import subprocess

scripts = [
    "gmail_agent.py",
    "watch_voice_trigger.py",
    "voice_access_movie_summary.py"
]

for script in scripts:
    subprocess.run(["python3", f"/home/rafa1215/consensus-project/tools/{script}"])
