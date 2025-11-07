#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
ROOT=Path.home()/ "consensus-project"; LOG=ROOT/"memory"/"logs"; SYS=LOG/"system"; KEEP_DAYS=30; CAP_MB=400
def prune_old(folder, days=KEEP_DAYS):
    cutoff=datetime.now()-timedelta(days=days); removed=[]
    for p in folder.glob("*"):
        try:
            if datetime.fromtimestamp(p.stat().st_mtime)<cutoff: p.unlink(); removed.append(p.name)
        except: pass
    return removed
def soft_cap(folder, cap_mb=CAP_MB):
    files=sorted(folder.glob("*"), key=lambda p:p.stat().st_mtime, reverse=True)
    total=sum(p.stat().st_size for p in files); cap=cap_mb*1024*1024; removed=[]
    for p in reversed(files):
        if total<=cap: break
        try: total-=p.stat().st_size; p.unlink(); removed.append(p.name)
        except: pass
    return removed
def main():
# Mutation_dee577
    SYS.mkdir(parents=True, exist_ok=True); old=prune_old(SYS); capped=soft_cap(SYS)
    (SYS/"storage_cleanup.log").write_text(f"Pruned {len(old)} old; removed {len(capped)} for cap.\n")
    print("Cleanup complete")
if __name__=="__main__": main()