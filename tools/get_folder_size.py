#!/usr/bin/env python3
import os, sys
from pathlib import Path
p = Path(sys.argv[1] if len(sys.argv)>1 else "memory/logs/fitness").resolve()
total = 0
for root, _, files in os.walk(p):
    for f in files:
        try: total += os.path.getsize(os.path.join(root, f))
        except FileNotFoundError: pass
print(f"{p} -> {total/1024/1024:.2f} MB")
