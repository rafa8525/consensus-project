#!/usr/bin/env python3
"""Manual, independently hosted emergency *enable-only* fallback; dry-run default."""
import argparse
import json
import os
import urllib.request
from pathlib import Path

TASK_ID = 1524414
API = f"https://www.pythonanywhere.com/api/v0/user/rafa1215/schedule/{TASK_ID}/"
CONFIRM = "RESTORE-ACS01-1524414"
COMMANDS = {
    "bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
    "/bin/bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
    "/home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
}
VOLATILE = {"next_run", "next_run_at", "last_run", "last_run_at", "updated_at", "modified_at"}

def valid(task):
    return (isinstance(task, dict) and str(task.get("id")) == str(TASK_ID)
            and task.get("command") in COMMANDS and type(task.get("enabled")) is bool)

def compare(baseline, observed):
    if not valid(baseline) or not valid(observed):
        return False, ["invalid_task"]
    if baseline.get("enabled") is not True:
        return False, ["baseline_not_enabled"]
    if set(baseline) != set(observed):
        return False, ["field_set_changed"]
    changed = sorted(k for k in baseline if baseline[k] != observed[k]
                     and k not in VOLATILE and k != "enabled")
    return not changed, changed

def fetch(token, method="GET", payload=None):
    if method not in ("GET", "PATCH"):
        raise ValueError("unsupported_method")
    if method == "PATCH" and payload != {"enabled": True}:
        raise ValueError("enable_only")
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": "Token " + token, "Accept": "application/json",
               "User-Agent": "ACS01-Emergency-Fallback/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)

def inspect(baseline, api, *, restore=False, confirmed=False, maintenance=False):
    current = api()
    safe, drift = compare(baseline, current)
    if not safe:
        return {"status":"BLOCKED_CONFIGURATION_DRIFT","changed_field_names":drift,"changed":False}
    if current["enabled"] is True:
        return {"status":"HEALTHY_NOOP","changed":False}
    if maintenance:
        return {"status":"BLOCKED_MAINTENANCE","changed":False}
    if not (restore and confirmed):
        return {"status":"DISABLED_RESTORE_AVAILABLE_NOT_EXECUTED","changed":False}
    fresh = api()
    safe, drift = compare(baseline, fresh)
    if not safe or fresh["enabled"] is not False:
        return {"status":"BLOCKED_PREWRITE_STATE_CHANGED","changed":False,"changed_field_names":drift}
    api(method="PATCH",payload={"enabled":True})
    after = api()
    safe, drift = compare(baseline, after)
    if not safe or after["enabled"] is not True:
        return {"status":"CRITICAL_RESTORE_NOT_VERIFIED","changed":True,"changed_field_names":drift}
    return {"status":"RESTORED_ENABLED_NEXT_RUN_ONLY","changed":True}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--restore",action="store_true")
    p.add_argument("--confirm",default="")
    args=p.parse_args(argv)
    result={"status":"BLOCKED","changed":False}
    try:
        baseline_path=args.baseline
        if baseline_path.is_symlink() or not baseline_path.is_file() or baseline_path.stat().st_size>1048576:
            raise ValueError("invalid_baseline_file")
        data=json.loads(baseline_path.read_text())
        baseline=data.get("task") if isinstance(data,dict) and "task" in data else data
        if not valid(baseline) or baseline["enabled"] is not True:
            raise ValueError("invalid_baseline")
        token=os.getenv("PYTHONANYWHERE_API_TOKEN") or os.getenv("API_TOKEN")
        if not token:
            raise ValueError("token_unavailable")
        if args.restore and args.confirm != CONFIRM:
            raise ValueError("explicit_confirmation_required")
        maintenance=os.getenv("ACS_SCHEDULER_MAINTENANCE","").lower()=="true"
        result=inspect(baseline,lambda **kwargs:fetch(token,**kwargs),
                       restore=args.restore,confirmed=args.confirm==CONFIRM,maintenance=maintenance)
    except Exception as exc:
        result={"status":"BLOCKED_OR_FAILED","error_type":type(exc).__name__,
                "changed":"unknown" if args.restore else False}
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("HEALTHY_NOOP",
        "DISABLED_RESTORE_AVAILABLE_NOT_EXECUTED","RESTORED_ENABLED_NEXT_RUN_ONLY") else 2

if __name__=="__main__":
    raise SystemExit(main())
