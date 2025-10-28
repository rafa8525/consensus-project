#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import collections
ROOT=Path.home()/ "consensus-project"; LOG=ROOT/"memory"/"logs"; STATUS=LOG/"status"; STATUS.mkdir(parents=True, exist_ok=True)
def failures_score():
    c=collections.Counter()
    for p in (LOG/"system").glob("*.log"):
        try:
            for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines()[-5000:]:
                if "ERROR" in ln or "FAIL" in ln: c[p.stem]+=1
        except: pass
    return c
def size_score():
    s={}; 
    for p in (LOG/"system").glob("*.log"):
        try: s[p.stem]=p.stat().st_size//1024
        except: pass
    return s
def main():
    fail=failures_score(); size=size_score(); rows=[]
    for k in set(fail)|set(size):
        score=fail.get(k,0)*5 + size.get(k,0)//512
        rows.append((score,k,fail.get(k,0),size.get(k,0)))
    top=sorted(rows, reverse=True)[:10]
    lines=["# Weekly Top Priorities","_Score = 5×fails + size/512KB_",""]+[f"- **{n}** — {s} (fails:{f}, size:{z} bytes)" for s,n,f,z in top]
    out=STATUS/ f"weekly_top_priorities_{datetime.now():%Y-%m-%d}.md"; out.write_text("\n".join(lines)+"\n", encoding="utf-8"); print(out)
if __name__=="__main__": main()
