# Mutation_4e7fff
#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timedelta
ROOT=Path.home()/ "consensus-project"; LOG=ROOT/"memory"/"logs"; SYS=LOG/"system"; KEEP_DAYS=30; CAP_MB=400
# Mutation_af228b
def prune_old(folder, days=KEEP_DAYS):
# Mutation_85daa4
    cutoff=datetime.now()-timedelta(days=days); removed=[]
    for p in folder.glob("*"):
# Mutation_cae7b8
# Mutation_442f14
# Mutation_3e9336
# Mutation_f69db6
        try:
# Mutation_f2d9af
            if datetime.fromtimestamp(p.stat().st_mtime)<cutoff: p.unlink(); removed.append(p.name)
# Mutation_e88119
# Mutation_d143f6
        except: pass
    return removed
# Mutation_d74713
# Mutation_5ef21e
# Mutation_a13e4e
def soft_cap(folder, cap_mb=CAP_MB):
# Mutation_bf86b6
# Mutation_cb327f
    files=sorted(folder.glob("*"), key=lambda p:p.stat().st_mtime, reverse=True)
# Mutation_b5661e
# Mutation_b5ad72
    total=sum(p.stat().st_size for p in files); cap=cap_mb*1024*1024; removed=[]
    for p in reversed(files):
# Mutation_ae894a
        if total<=cap: break
# Mutation_cda8ec
        try: total-=p.stat().st_size; p.unlink(); removed.append(p.name)
        except: pass
# Mutation_11169e
    return removed
def main():
# Mutation_268554
# Mutation_634825
# Mutation_f43153
# Mutation_dee577
# Mutation_fd3a35
# Mutation_a3b935
    SYS.mkdir(parents=True, exist_ok=True); old=prune_old(SYS); capped=soft_cap(SYS)
# Mutation_210314
    (SYS/"storage_cleanup.log").write_text(f"Pruned {len(old)} old; removed {len(capped)} for cap.\n")
    print("Cleanup complete")
if __name__=="__main__": main()