#!/usr/bin/env python3
"""Non-destructive ACS verification: distinguish runtime churn from source changes."""
import ast
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "consensus-project"
RUNTIME_PREFIXES = ("memory/", "logs/")
RUNTIME_SINGLETONS = ("scheduled_goal.txt",)
BACKUP_MARKERS = (".pre-", ".before_", ".pre_", ".backup", ".bak")
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, text=True,
                          capture_output=True, timeout=90, check=False)
def classify():
    proc=git("status", "--porcelain=v1", "--untracked-files=all")
    if proc.returncode:
        raise RuntimeError("git status failed")
    out={"runtime_modified":[],"runtime_untracked":[],"source_modified":[],
         "source_untracked":[],"backup_candidates":[]}
    for line in proc.stdout.splitlines():
        if len(line)<4:
            continue
        xy=line[:2]
        path=line[3:]
        if " -> " in path:
            path=path.rsplit(" -> ",1)[-1]
        if path.startswith(RUNTIME_PREFIXES) or path in RUNTIME_SINGLETONS:
            bucket="runtime_untracked" if xy=="??" else "runtime_modified"
        elif any(marker in path for marker in BACKUP_MARKERS):
            bucket="backup_candidates"
        else:
            bucket="source_untracked" if xy=="??" else "source_modified"
        out[bucket].append(path)
    return out
def agent_state(agent):
    path=ROOT/"memory"/"agents"/(agent.lower().replace("-","")+"_state.json")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
        stamp=dt.datetime.fromisoformat(data["finished_at_utc"].replace("Z","+00:00"))
        age=(dt.datetime.now(dt.timezone.utc)-stamp).total_seconds()/3600
        return {"healthy":data.get("status")=="healthy" and 0<=age<=36,
                "age_hours":round(age,2),"status":data.get("status")}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"healthy":False,"error":type(exc).__name__}
def main():
    if not (ROOT/".git").exists():
        print(json.dumps({"mode":"READ_ONLY","error":"repository_missing"}))
        return 2
    branch=git("branch","--show-current")
    diverge=git("rev-list","--left-right","--count","HEAD...origin/v1.1-dev")
    try:
        counts=[int(x) for x in diverge.stdout.strip().split()]
        sync=diverge.returncode==0 and counts==[0,0]
    except ValueError:
        counts=[]
        sync=False
    changes=classify()
    syntax={}
    for path in ("agents/supervisor.py","agents/run_acs_cycle.py",
                 "agents/safe_sync_live_branch.py","agents/pythonanywhere_health_bridge.py"):
        try:
            ast.parse((ROOT/path).read_text(encoding="utf-8"))
            syntax[path]=True
        except (OSError,SyntaxError,UnicodeError):
            syntax[path]=False
    states={agent:agent_state(agent) for agent in ("ACS-02","ACS-03","ACS-04","ACS-05")}
    source_review=bool(changes["source_modified"] or changes["source_untracked"])
    ok=(branch.returncode==0 and branch.stdout.strip()=="v1.1-dev"
        and sync and all(syntax.values()) and all(x["healthy"] for x in states.values()))
    payload={"mode":"READ_ONLY","branch":branch.stdout.strip(),
             "remote_branch_synced":sync,"ahead_behind":counts,
             "agent_states":states,"syntax":syntax,
             "working_tree":{"counts":{k:len(v) for k,v in changes.items()},
                             "source_review_required":source_review,
                             "source_modified":changes["source_modified"],
                             "source_untracked":changes["source_untracked"],
                             "backup_candidates":changes["backup_candidates"]},
             "runtime_changes_preserved":True,
             "verification_passed":ok,
             "note":"Source review required is advisory. No file was changed."}
    print(json.dumps(payload,indent=2))
    return 0 if ok else 2
if __name__=="__main__":
    raise SystemExit(main())
