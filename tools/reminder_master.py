# Mutation_97b6ec
#!/usr/bin/env python3
import subprocess, os

BASE = "/home/rafa1215/consensus-project/tools"

subprocess.run(["python3", f"{BASE}/daily_voice_reminder.py"])
subprocess.run(["python3", f"{BASE}/reminder_scheduler_loop.py"])