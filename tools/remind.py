#!/usr/bin/env python3
import re,json,time,argparse
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MEM=ROOT/"memory"; CONF=MEM/"config"; CONF.mkdir(parents=True,exist_ok=True)
REM=CONF/"reminders.json"; LOGD=MEM/"logs"/"reminders"; LOGD.mkdir(parents=True,exist_ok=True)
def when(s):
  s=s.strip().lower(); now=datetime.utcnow()
  m=re.match(r"in\s+(\d+)\s*m",s);  # in Xm
  if m: return int((now+timedelta(minutes=int(m.group(1)))).timestamp())
  m=re.match(r"in\s+(\d+)\s*h",s);  # in Xh
  if m: return int((now+timedelta(hours=int(m.group(1)))).timestamp())
  m=re.match(r"in\s+(\d+)\s*d",s);  # in Xd
  if m: return int((now+timedelta(days=int(m.group(1)))).timestamp())
  m=re.match(r"(today\s+)?(\d{1,2}):(\d{2})(\s*(am|pm))?$",s)
  if m:
    h=int(m.group(2)); mi=int(m.group(3)); ap=(m.group(5) or "").lower()
    if ap=="pm" and h<12: h+=12
    if ap=="am" and h==12: h=0
    dt=now.replace(hour=h,minute=mi,second=0,microsecond=0)
    if dt.timestamp()<now.timestamp(): dt+=timedelta(days=1)
    return int(dt.timestamp())
  m=re.match(r"tomorrow\s+(\d{1,2}):(\d{2})(\s*(am|pm))?$",s)
  if m:
    h=int(m.group(1)); mi=int(m.group(2)); ap=(m.group(4) or "").lower()
    if ap=="pm" and h<12: h+=12
    if ap=="am" and h==12: h=0
    dt=now.replace(hour=h,minute=mi,second=0,microsecond=0)+timedelta(days=1)
    return int(dt.timestamp())
  m=re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})$",s)  # UTC absolute
  if m: return int(datetime(*map(int,m.groups())).timestamp())
  raise SystemExit(f"Unable to parse --when: {s}")
def load():
  return json.loads(REM.read_text(encoding="utf-8")) if REM.exists() else {"items":[]}
def save(d):
  tmp=REM.with_suffix(".tmp"); tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(REM)
def main():
  ap=argparse.ArgumentParser(); ap.add_argument("--text",required=True); ap.add_argument("--when",required=True); ap.add_argument("--channel",default="log",choices=["log","twilio","both"])
  a=ap.parse_args(); due=when(a.when); db=load(); rid=f"r{int(time.time())}"
  db["items"].append({"id":rid,"text":a.text,"due_ts":due,"channel":a.channel,"sent_ts":None}); save(db)
  with open(MEM/"logs"/"reminders"/"reminder_log.txt","a",encoding="utf-8") as f:
    f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}] scheduled id={rid} due_ts={due} text={a.text}\n")
  print(f"OK scheduled id={rid} due_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(due))}  {a.text}")
if __name__=="__main__": main()
