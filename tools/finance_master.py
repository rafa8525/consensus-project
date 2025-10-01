#!/usr/bin/env python3
import subprocess, os

BASE = "/home/rafa1215/consensus-project/tools"

subprocess.run(["python3", f"{BASE}/finance_media.py"])
subprocess.run(["python3", f"{BASE}/finance_audit.py"])
