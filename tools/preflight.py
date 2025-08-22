#!/usr/bin/env python3
import os, platform, datetime
ROOT="."
LOG="logs/project/preflight.log"
REQ={
 "python": "/usr/bin/python3",
 "dispatcher": os.path.join(ROOT,"tools/consensus_dispatcher.py"),
 "registry": os.path.join(ROOT, os.environ.get("CONSENSUS_REGISTRY","CONSENSUS_REGISTRY.yaml")),
 "ensure_dirs": os.path.join(ROOT,"tools/ensure_dirs.sh"),
}
os.makedirs(os.path.dirname(LOG), exist_ok=True)
with open(LOG,"w") as f:
  f.write(f"[preflight] {datetime.datetime.now()}\n")
  f.write(f"python_exists={os.path.exists(REQ['python'])} path={REQ['python']}\n")
  for k,v in REQ.items(): f.write(f"{k}_exists={os.path.exists(v)} path={v}\n")
  f.write(f"cwd={os.getcwd()} platform={platform.platform()}\n")
print(LOG)
