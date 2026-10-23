#!/usr/bin/env python3
"""Read-only ACS reliability gate; never resets, merges, pushes, or restarts."""
import ast, datetime as dt, json, subprocess, sys
from pathlib import Path
ROOT=Path.home()/"consensus-project"
def git(*args):
    p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,timeout=30)
    return p.returncode,p.stdout.strip()
def main():
    checks={}
    if not (ROOT/".git").exists():
        print("Missing repository",file=sys.stderr); return 2
    code,branch=git("branch","--show-current")
    checks["correct_branch"]=code==0 and branch=="v1.1-dev"
    code,dirty=git("status","--porcelain")
    checks["git_inspection"]=code==0
    checks["worktree_clean"]=not bool(dirty)
    code,div=git("rev-list","--left-right","--count","HEAD...origin/v1.1-dev")
    checks["remote_branch_synced"]=code==0 and div.split()==["0","0"]
    checks["agent_states"]={}
    for name in ("ACS-02","ACS-03","ACS-04","ACS-05"):
        path=ROOT/"memory"/"agents"/(name.lower().replace("-","")+"_state.json")
        try:
            data=json.loads(path.read_text())
            stamp=dt.datetime.fromisoformat(data["finished_at_utc"].replace("Z","+00:00"))
            age=(dt.datetime.now(dt.timezone.utc)-stamp).total_seconds()/3600
            checks["agent_states"][name]={"healthy":data.get("status")=="healthy" and 0<=age<=36,"age_hours":round(age,1),"status":data.get("status")}
        except (OSError,KeyError,ValueError,TypeError) as exc:
            checks["agent_states"][name]={"healthy":False,"error":type(exc).__name__}
    syntax={}
    for path in ("agents/supervisor.py","agents/run_acs_cycle.py","agents/safe_sync_live_branch.py","agents/pythonanywhere_health_bridge.py"):
        try: ast.parse((ROOT/path).read_text()); syntax[path]=True
        except (OSError,SyntaxError,UnicodeError): syntax[path]=False
    checks["syntax"]=syntax
    print(json.dumps({"mode":"READ_ONLY","checks":checks},indent=2))
    return 0 if (checks["correct_branch"] and checks["git_inspection"] and checks["remote_branch_synced"] and all(v["healthy"] for v in checks["agent_states"].values()) and all(syntax.values())) else 2
if __name__=="__main__": raise SystemExit(main())
