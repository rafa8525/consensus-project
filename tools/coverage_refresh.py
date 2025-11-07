#!/usr/bin/env python3
import os,re,time,yaml,sys
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
W=['tools','agents','core','services','scripts']
OUT=os.path.join(R,'memory/logs/status/github_coverage.md')
GAP=os.path.join(R,'memory/logs/status/github_gaps.txt')
SCHED=os.path.join(R,'schedule_utc.txt')
REGS=[os.path.join(R,p) for p in ('CONSENSUS_REGISTRY.yaml','CONSENSUS_REGISTRY_v2.yaml','config/CONSENSUS_REGISTRY.yaml')]
def is_entry(p):
    try:
        s=open(p,'r',encoding='utf-8',errors='ignore').read(15000)
        return ('__main__' in s) or ('argparse' in s.lower()) or re.search(r'\bdef\s+main\s*\(',s)
    except: return False
all_py=[]
for root in W:
    rp=os.path.join(R,root)
    if not os.path.isdir(rp): continue
    for a,_,files in os.walk(rp):
        if any(t in a for t in ('.git','__pycache__','archive','backup','test')): continue
        for fn in files:
            if fn.endswith('.py') and not fn.startswith('_'):
                all_py.append(os.path.relpath(os.path.join(a,fn),R))
sched=set()
if os.path.exists(SCHED):
    for ln in open(SCHED,encoding='utf-8',errors='ignore'):
        m=re.search(r'python[0-9.]*\s+([^\s]+\.py)',ln)
        if m: sched.add(os.path.normpath(m.group(1)))
reg=set()
for rf in REGS:
    if os.path.exists(rf):
        try:
            d=yaml.safe_load(open(rf,encoding='utf-8')) or {}
            for v in (d.get('agents',{}) or {}).values():
                if isinstance(v,dict) and v.get('path'): reg.add(v['path'])
        except: pass
rows=[]; gaps=[]
for rel in sorted(set(all_py)):
    entry='YES' if is_entry(os.path.join(R,rel)) else 'no'
    on='YES' if rel in sched else 'no'
    inr='YES' if rel in reg else 'no'
    rows.append((rel,entry,on,inr))
    if entry=='YES' and on=='no' and inr=='no':
        gaps.append(rel)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("# GitHub Coverage Report (Whitelist)\n")
    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime())}\n\n")
    f.write(f"Dirs: {', '.join(W)}\n")
    f.write(f"Total .py: **{len(all_py)}** | Entry-like: **{sum(1 for r in rows if r[1]=='YES')}**\n")
    f.write(f"On schedule: **{sum(1 for r in rows if r[2]=='YES')}** | In registry: **{sum(1 for r in rows if r[3]=='YES')}**\n")
    f.write("| File | Entry | Scheduled | In Registry |\n|---|---:|---:|---:|\n")
    for rel,entry,on,inr in rows:
        f.write(f"| `{rel}` | {entry} | {on} | {inr} |\n")
    f.write("\n## " + ("✅ No gaps\n" if not gaps else "Missing BOTH schedule & registry\n" + "\n".join(f"- {g}" for g in gaps)))
with open(GAP,'w',encoding='utf-8') as f: f.write("\n".join(gaps))
print(f"Wrote {OUT} and {GAP}")
