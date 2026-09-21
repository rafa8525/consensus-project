#!/usr/bin/env python3
"""Durable ACS-02..ACS-05 execution harness.

Runs the existing cycle components, writes one authoritative JSON state file per
ACS role, and never converts a failed component into a successful result.
Designed for PythonAnywhere scheduling and ACS-01/health-bridge verification.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

REPO=Path.home()/"consensus-project"
STATE=REPO/"memory"/"agents"
PY=sys.executable
CYCLES={
 "ACS-02": [("absorption", REPO/"memory/public/absorption_last_success.json", "evidence")],
 "ACS-03": [
   ("fitness_tracking_verifier", REPO/"tools/fitness_tracking_verifier.py", "script"),
   ("health_master", REPO/"tools/health_master.py", "script"),
   ("backup_fitness", REPO/"tools/backup_fitness.py", "script"),
 ],
 "ACS-04": [("infrastructure_guardian", REPO/"agents/infrastructure_guardian.py", "script")],
 "ACS-05": [("continuity_guardian", REPO/"agents/continuity_guardian_agent.py", "script")],
}
def now(): return datetime.now(timezone.utc).isoformat()
def run_one(name,path,kind):
 if kind=="evidence":
  try:
   data=json.loads(path.read_text())
   ok=data.get("status")=="ok"
   return {"component":name,"ok":ok,"source":str(path),"detail":data.get("last_success_utc")}
  except Exception as e: return {"component":name,"ok":False,"source":str(path),"error":f"{type(e).__name__}: {e}"}
 cmd=[PY,str(path)]
 if name=="continuity_guardian": cmd.append("--force")
 try:
  p=subprocess.run(cmd,cwd=REPO,text=True,capture_output=True,timeout=900)
  # Infrastructure Guardian uses 0 healthy, 1 warning, 2 critical, 3 execution failure.
  ok=p.returncode==0 if name!="infrastructure_guardian" else p.returncode in (0,1)
  return {"component":name,"ok":ok,"returncode":p.returncode,
          "stdout":p.stdout[-2000:],"stderr":p.stderr[-2000:]}
 except Exception as e: return {"component":name,"ok":False,"error":f"{type(e).__name__}: {e}"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("agent",choices=sorted(CYCLES)); args=ap.parse_args()
 started=now(); results=[run_one(*x) for x in CYCLES[args.agent]]
 ok=all(x["ok"] for x in results); finished=now()
 payload={"agent":args.agent,"started_at_utc":started,"finished_at_utc":finished,
          "status":"ok" if ok else "degraded","verified":True,"results":results}
 STATE.mkdir(parents=True,exist_ok=True)
 target=STATE/f"{args.agent.lower().replace('-','')}_state.json"
 tmp=target.with_suffix(".tmp"); tmp.write_text(json.dumps(payload,indent=2)+"\n"); os.replace(tmp,target)
 print(json.dumps(payload))
 return 0 if ok else 2
if __name__=="__main__": raise SystemExit(main())
