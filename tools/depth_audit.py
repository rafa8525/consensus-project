#!/usr/bin/env python3
import os, time, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_MD = os.path.join(ROOT, "memory/logs/status/depth_audit.md")
LOG_SYS = os.path.join(ROOT, "memory/logs/system/depth_audit.log")
EXCLUDE = {".git","__pycache__","node_modules",".venv","venv","env",".mypy_cache",".pytest_cache",".idea",".vscode","dist","build"}

def discover():
    out=[]
    for r,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
        for fn in files:
            if fn.endswith(".py"):
                out.append(os.path.relpath(os.path.join(r,fn), ROOT))
    return sorted(set(out))

def main():
    files = discover()
    os.makedirs(os.path.dirname(LOG_SYS), exist_ok=True)
    with open(LOG_SYS,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":time.time(),"found":len(files)})+"\n")
    os.makedirs(os.path.dirname(LOG_MD), exist_ok=True)
    with open(LOG_MD,"w",encoding="utf-8") as f:
        f.write("# Depth Audit (Minimal)\n")
        f.write("Generated: "+time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())+"\n\n")
        f.write("Discovered .py files: **"+str(len(files))+"**\n\n")
        f.write("| File |\n|---|\n")
        for rel in files:
            f.write(f"| `{rel}` |\n")
    # Always exit 0 in interactive runs
    # Use AUDIT_STRICT=1 in cron/guard later if you want hard failures.
    if os.environ.get("AUDIT_STRICT")=="1" and not files:
        raise SystemExit(1)
    raise SystemExit(0)

if __name__=="__main__": main()
