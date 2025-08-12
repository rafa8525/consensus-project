#!/usr/bin/env python3
import json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MEM=ROOT/"memory"; CONF=MEM/"config"; REM=CONF/"reminders.json"
LOGD=MEM/"logs"/"reminders"; LOGD.mkdir(parents=True,exist_ok=True)
def load(): return json.loads(REM.read_text(encoding="utf-8")) if REM.exists() else {"items":[]}
def save(d):
  tmp=REM.with_suffix(".tmp"); tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(REM)
def deliver(it):
  line=f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}] REMIND id={it['id']} text={it['text']}"
  p=LOGD/"due.log"; p.write_text("",encoding="utf-8") if not p.exists() else None
  with open(p,"a",encoding="utf-8") as f: f.write(line+"\n")
  return True
def main():
  db=load(); now=int(time.time()); changed=False
  for it in db.get("items",[]):
    if it.get("sent_ts"): continue
    if now>=int(it["due_ts"]):
      if deliver(it): it["sent_ts"]=int(time.time()); changed=True
  if changed: save(db)
if __name__=="__main__": main()
