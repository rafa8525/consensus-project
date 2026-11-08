#!/usr/bin/env python3
"""Independent ACS-01 schedule guard: read-only unless --apply --allow-enable.
PythonAnywhere schedule API permits re-enabling, not a run-now invocation.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone

USER = "rafa1215"
TASK_ID = 1524414
ALLOWED_COMMANDS = {
    "bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
    "/bin/bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
    "/home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
}
REPORT_URL = ("https://raw.githubusercontent.com/rafa8525/consensus-project/"
              "main/logs/system/pythonanywhere_health.json")
API_URL = f"https://www.pythonanywhere.com/api/v0/user/{USER}/schedule/{TASK_ID}/"
MAX_AGE_SECONDS = 27 * 3600

def fetch_json(url, token=None, method="GET", body=None, opener=None):
    headers = {"User-Agent": "ACS-Schedule-Guard", "Cache-Control": "no-cache"}
    if token:
        headers["Authorization"] = "Token " + token
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with (opener or urllib.request.urlopen)(request, timeout=25) as response:
        return json.load(response)

def inspect_report(report, now):
    if not isinstance(report, dict):
        return "invalid_report"
    try:
        ts = datetime.fromisoformat(report["generated_at_utc"].replace("Z","+00:00"))
        if ts.tzinfo is None:
            return "invalid_report_timestamp"
        age = (now-ts).total_seconds()
        if age < 0:
            return "future_dated_report"
        if age > MAX_AGE_SECONDS:
            return "stale_report"
    except (KeyError, AttributeError, ValueError, TypeError):
        return "invalid_report_timestamp"
    agents = report.get("agents")
    if not isinstance(agents, dict):
        return "missing_agents"
    for name in ("ACS-01","ACS-02","ACS-03","ACS-04","ACS-05"):
        a = agents.get(name)
        if not isinstance(a, dict) or a.get("verified") is not True or a.get("status") != "current" or a.get("health_status") not in ("ok","healthy"):
            return "unhealthy_agents"
    return "healthy"

def validate_task(task):
    if not isinstance(task, dict) or str(task.get("id")) != str(TASK_ID):
        return "unexpected_task_id"
    cmd = task.get("command")
    if not isinstance(cmd, str) or cmd.strip() not in ALLOWED_COMMANDS:
        return "unexpected_command"
    if task.get("enabled") not in (True,False):
        return "invalid_enabled"
    return None

def decide(report_status, task):
    issue = validate_task(task)
    if issue:
        return "BLOCKED_" + issue
    if task["enabled"] is True:
        return "HEALTHY_NOOP" if report_status == "healthy" else "ESCALATE_ENABLED_BUT_" + report_status
    if report_status in ("healthy","stale_report","unhealthy_agents"):
        return "ENABLE_DISABLED_TASK"
    return "BLOCKED_" + report_status

def guard(apply=False, allow_enable=False, token=None, now=None, fetcher=fetch_json, maintenance=False):
    now = now or datetime.now(timezone.utc)
    if not token:
        return {"status":"BLOCKED_missing_api_token","changed":False}
    report = fetcher(REPORT_URL)
    status = inspect_report(report,now)
    before = fetcher(API_URL, token=token)
    decision = decide(status,before)
    result = {"status":decision,"report_status":status,"changed":False,"task_id":TASK_ID,
              "mode":"apply" if apply else "dry_run"}
    if decision != "ENABLE_DISABLED_TASK" or not apply:
        return result
    if not allow_enable:
        result["status"]="BLOCKED_apply_requires_allow_enable"
        return result
    if maintenance:
        result["status"]="BLOCKED_explicit_maintenance_mode"
        return result
    latest = fetcher(API_URL,token=token)
    if latest != before or validate_task(latest) or latest["enabled"] is not False:
        result["status"]="BLOCKED_prewrite_schedule_changed"
        return result
    # ONLY change the enabled flag; never change task command or timing.
    fetcher(API_URL, token=token, method="PATCH", body={"enabled":True})
    result["changed"]=True  # PATCH has been attempted; verification still required
    after=fetcher(API_URL,token=token)
    if validate_task(after) or after.get("enabled") is not True:
        result["status"]="ESCALATE_postwrite_verification_failed"
        return result
    # The sole allowed metadata delta is enabled: False -> True.
    before_metadata={k:v for k,v in before.items() if k!="enabled"}
    after_metadata={k:v for k,v in after.items() if k!="enabled"}
    if after_metadata != before_metadata:
        result["status"]="ESCALATE_configuration_change"
        return result
    result["status"]="SCHEDULE_REENABLED_NEXT_RUN_ONLY"
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apply",action="store_true")
    p.add_argument("--allow-enable",action="store_true")
    args=p.parse_args()
    try:
        result=guard(args.apply,args.allow_enable,os.getenv("PYTHONANYWHERE_API_TOKEN"),
                     maintenance=os.getenv("ACS_SCHEDULER_MAINTENANCE","").lower()=="true")
    except (urllib.error.URLError,OSError,TimeoutError,ValueError) as exc:
        result={"status":"ESCALATE_api_or_network_error","error_type":type(exc).__name__,"changed":"unknown"}
        if isinstance(exc, urllib.error.HTTPError):
            result["http_status"] = exc.code  # HTTP status only: never print token or response body
            result["request_host"] = urlparse(exc.url).hostname  # host only; no path, query or token
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("HEALTHY_NOOP","SCHEDULE_REENABLED_NEXT_RUN_ONLY") else 2

if __name__=="__main__":
    sys.exit(main())
