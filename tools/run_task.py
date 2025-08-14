#!/usr/bin/env python3
import os, json, sys, subprocess
from pathlib import Path
env = Path("/home/rafa1215/.pa_env.json")
if env.exists():
    os.environ.update({k: str(v) for k, v in json.loads(env.read_text()).items()})
root = "/home/rafa1215/consensus-project"
cmd = sys.argv[1:] or ["python3", "-V"]
sys.exit(subprocess.run(cmd, cwd=root).returncode)
