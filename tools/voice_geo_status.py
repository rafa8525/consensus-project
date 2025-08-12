#!/usr/bin/env python3
import re, glob
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parent.parent
GDIR=ROOT/"memory"/"logs"/"geofencing"
def parse_iso(s):
    try: return datetime.fromisoformat(s.replace("Z","+00:00"))
    except: return None
def last_heartbeat():
    files=sorted(GDIR.glob("heartbeat_*.md"))
    if not files: return None, None
    last=files[-1]; ts=None
    for line in reversed(last.read_text(encoding="utf-8").splitlines()):
        m=re.match(r"\[([^]]+)\]", line.strip())
        if m: ts=parse_iso(m.group(1)); break
    return ts, last.name
def last_event():
    p=GDIR/"geofence_events.log"
    if not p.exists(): return None, None
    for line in reversed(p.read_text(encoding="utf-8").splitlines()):
        m=re.match(r"\[([^]]+)\]\s+(.*)$", line.strip())
        if m: return parse_iso(m.group(1)), m.group(2)
    return None, None
def main():
    now=datetime.now(timezone.utc)
    hb_ts,hb_file=last_heartbeat()
    ev_ts,ev_txt=last_event()
    out=[]
    if hb_ts:
        ago=now-hb_ts; mins=int(ago.total_seconds()//60)
        out.append(f"Geofence heartbeat {mins}m ago ({hb_ts.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}) from {hb_file}.")
    else:
        out.append("No geofence heartbeat found.")
    if ev_ts:
        ago=now-ev_ts; mins=int(ago.total_seconds()//60)
        out.append(f"Last geofence event {mins}m ago ({ev_ts.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}): {ev_txt}")
    else:
        out.append("No geofence events logged yet.")
    print(" ".join(out))
if __name__=="__main__": main()
