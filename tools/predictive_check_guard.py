#!/usr/bin/env python3
import shutil, os, sys
from pathlib import Path
from datetime import datetime
ROOT = Path.home()/ "consensus-project"; STATUS = ROOT/"memory"/"logs"/"status"; STATUS.mkdir(parents=True, exist_ok=True)
def check_disk(min_free_mb=300):
    u=shutil.disk_usage("/"); free=u.free//(1024*1024); return free>=min_free_mb, f"Disk free: {free} MB (min {min_free_mb})"
def check_env():
    must=[]; missing=[k for k in must if not os.getenv(k)]; 
    return (len(missing)==0, "All env present" if not missing else f"Missing env: {missing}")
def main():
    res=[check_disk(), check_env()]; ok=all(r[0] for r in res)
    lines=[f"# Predictive Check — {datetime.now():%Y-%m-%d %H:%M:%S}"]+[f"- {['disk','env'][i]}: {'OK' if r[0] else 'BLOCK'} — {r[1]}" for i,r in enumerate(res)]
    out=STATUS/ f"predictive_check_{datetime.now():%Y-%m-%d}.md"; out.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(out); sys.exit(0 if ok else 2)
if __name__=="__main__": main()
