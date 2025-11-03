#!/usr/bin/python3
import subprocess

scripts = [
    "fitness_tracker.py",
    "hot_weather_swim_agent.py",
    "swim_weather_nudge.py"
]

for script in scripts:
    subprocess.run(["python3", f"/home/rafa1215/consensus-project/tools/{script}"])
