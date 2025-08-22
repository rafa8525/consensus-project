#!/usr/bin/env python3
import os, glob, csv, datetime
ROOT="."
OUT="logs/reports/status.log"
CANDIDATE_DIRS=[os.path.join(ROOT,"csv"), os.path.join(ROOT,"memory","agents"), os.path.join(ROOT,"memory","logs","repair")]
def newest():
  c=[]
  for d in CANDIDATE_DIRS:
    if os.path.isdir(d): c+=glob.glob(os.path.join(d,"agent_learnings_*.csv"))
  return sorted(c)[-1] if c else None
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT,"a") as f:
  f.write(f"[status] {datetime.datetime.now()}\n")
  p=newest()
  if p and os.path.exists(p):
    f.write(f"ingested={p}\n")
    rows=list(csv.DictReader(open(p)))
    for r in rows[:5]:
      f.write(f"- #{r.get('Agent #')} {r.get('Agent Name')}: {r.get('Learning (Today)')}\n")
  else:
    f.write("no agent_learnings_*.csv found\n")
print(OUT)
