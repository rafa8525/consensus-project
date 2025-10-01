#!/usr/bin/env python3
import subprocess, os, sys

BASE = "/home/rafa1215/consensus-project/tools"

try:
    subprocess.run(["python3", f"{BASE}/parse_food_log_sheet.py"], check=True)
except Exception as e:
    print(f"parse_food_log_sheet.py failed: {e}")

try:
    subprocess.run(["python3", f"{BASE}/nutrition_fallback.py"], check=True)
except Exception as e:
    print(f"nutrition_fallback.py failed: {e}")
