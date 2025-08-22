#!/usr/bin/env python3
import os, json, datetime, subprocess, sys
ROOT="."
LEDGER=os.path.join(ROOT,"memory/logs/repair/ledger.json")
DISPATCHER=os.path.join(ROOT,"tools/consensus_dispatcher.py")
def now(): return datetime.datetime.now()
def key(): return now().strftime("%Y-%m-%d")
def load(): 
  try: return json.load(open(LEDGER))
  except: return {}
def save(d):
  os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
  json.dump(d, open(LEDGER,"w"), indent=2)
def run(window):
  env=os.environ.copy(); env["WINDOW"]=window
  p=subprocess.Popen([sys.executable, DISPATCHER], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, cwd=ROOT)
  out,err=p.communicate(); return p.returncode,out,err
if __name__=="__main__":
  assert len(sys.argv)>1 and sys.argv[1] in ("am","pm","weekly","monthly"), "Usage: catchup_guard.py <am|pm|weekly|monthly>"
  w=sys.argv[1]; led=load(); day=key(); rec=led.get(day,{})
  if rec.get(w,{}).get("ok"): sys.exit(0)
  rc,out,err=run(w); ok=(rc==0)
  rec[w]={"ok":ok,"rc":rc,"ts":now().strftime("%Y-%m-%d %H:%M:%S")}
  led[day]=rec; save(led)
  open(f"logs/project/{w}_catchup.log","a").write(out)
  if err: open(f"logs/project/{w}_catchup.err","a").write(err)
  print(out); sys.exit(rc)
