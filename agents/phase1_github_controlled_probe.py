#!/usr/bin/env python3
"""GitHub-hosted controlled ACS-01 recovery probe. No production changes by default.

A live test requires a workflow_dispatch on main and an explicit confirmation phrase.
Tests only schedule re-enablement, not genuine unattended scheduled recovery.
"""
import argparse
import json
import os
import signal
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import phase1_independent_schedule_guard as g

CONFIRM="TEST-ACS01-1524414"
EVIDENCE=Path("phase1_github_controlled_probe_evidence.json")
CORE_FIELDS=("id","command","interval","hour","minute","description")
UTC=timezone.utc

def snapshot(now=None):
    now=now or datetime.now(UTC)
    return {"observed_at_utc":now.isoformat(),"task_id":g.TASK_ID,
            "scope":"github_controlled_production_probe",
            "unattended_scheduler_recovery_proven":False,
            "production_recovery_certified":False,
            "disable_attempted":False,"restoration_verified":False,
            "recovery_status":"NOT_RUN","status":"NOT_RUN"}

def report(event, facts):
    facts["status"]=event
    EVIDENCE.write_text(json.dumps(facts,sort_keys=True,indent=2)+"\n")

def eligible_utc(t):
    return not ((t.hour==17 and t.minute>=30) or
                (t.hour==18 and t.minute<30))

def test_preflight(environment, now):
    if environment.get("GITHUB_EVENT_NAME")!="workflow_dispatch":
        return "not_manual_dispatch"
    if environment.get("GITHUB_REF")!="refs/heads/main":
        return "not_main_branch"
    if environment.get("ACS_LIVE_TEST_CONFIRM")!=CONFIRM:
        return "missing_exact_confirmation"
    if environment.get("ACS_SCHEDULER_MAINTENANCE","").lower()=="true":
        return "maintenance_mode"
    if environment.get("ACS_SCHEDULER_RECOVERY_ENABLED","").lower()=="true":
        return "automatic_recovery_switch_must_remain_off"
    if not eligible_utc(now):
        return "scheduled_execution_window"
    if not environment.get("PYTHONANYWHERE_API_TOKEN"):
        return "missing_pythonanywhere_api_token"
    return None

def safe_task(task,enabled):
    return g.validate_task(task) is None and task.get("enabled") is enabled

def verify_diff(before,after):
    return g.task_configuration_diff(before,after)["safe"]

def restore_if_needed(before,token,fetcher=g.fetch_json,attempts=3):
    """Best-effort emergency restoration. Raises unless enabled and core preserved."""
    problems=[]
    for n in range(attempts):
        try:
            state=fetcher(g.API_URL,token=token)
            if safe_task(state,True) and verify_diff(before,state):
                return True
            if g.validate_task(state):
                raise RuntimeError("refuse_to_mutate_unexpected_task")
            # PATCH only approved enabled flag. Never mutate command/schedule.
            fetcher(g.API_URL,token=token,method="PATCH",body={"enabled":True})
            after=fetcher(g.API_URL,token=token)
            if safe_task(after,True) and verify_diff(before,after):
                return True
            problems.append("restore_validation_failed")
        except Exception as exc:
            problems.append(type(exc).__name__)
    raise RuntimeError("restoration_not_verified")

def controlled_probe(token,fetcher=g.fetch_json, now=None):
    now=now or datetime.now(UTC)
    info=snapshot(now)
    before=fetcher(g.API_URL,token=token)
    if not safe_task(before,True):
        info["status"]="BLOCKED_preflight_unexpected_task"
        return info
    remote=fetcher(g.REPORT_URL)
    if g.inspect_report(remote,now)!="healthy":
        info["status"]="BLOCKED_preflight_unhealthy_report"
        return info
    confirmed=fetcher(g.API_URL,token=token)
    if not safe_task(confirmed,True) or not verify_diff(before,confirmed):
        info["status"]="BLOCKED_preflight_configuration_drift"
        return info
    before=confirmed
    info["preflight_verified"]=True
    # Never upload raw task configuration. Keep the exact baseline in process RAM.
    disable_attempted=False
    try:
        disable_attempted=True
        info["disable_attempted"]=True
        fetcher(g.API_URL,token=token,method="PATCH",body={"enabled":False})
        disabled=fetcher(g.API_URL,token=token)
        if not safe_task(disabled,False) or not verify_diff(before,disabled):
            info["status"]="FAILED_disable_verification"
            info["disable_changed_field_names"]=g.task_configuration_diff(before,disabled)["configuration"]
            return info
        info["disabled_state_verified"]=True
        recovery=g.guard(True,True,token,now,fetcher=fetcher)
        info["recovery_status"]=recovery["status"]
        final=fetcher(g.API_URL,token=token)
        if recovery["status"]!="SCHEDULE_REENABLED_NEXT_RUN_ONLY":
            info["status"]="FAILED_controller_response"
        elif not safe_task(final,True) or not verify_diff(before,final):
            info["status"]="FAILED_configuration_after_recovery"
            info["recovery_changed_field_names"]=g.task_configuration_diff(before,final)["configuration"]
        else:
            info["status"]="GITHUB_INITIATED_SCHEDULE_REENABLE_VERIFIED"
        return info
    finally:
        if disable_attempted:
            info["restoration_verified"]=restore_if_needed(before,token,fetcher)
            info["restoration_checked_at_utc"]=datetime.now(UTC).isoformat()
            if not info["restoration_verified"]:
                info["status"]="CRITICAL_restore_unverified"

def simulated_probe():
    now=datetime(2026,11,8,3,15,tzinfo=UTC)
    info=snapshot(now)
    store={"id":g.TASK_ID,
           "command":"bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
           "enabled":True,"interval":"daily","hour":10,"minute":0,
           "next_run":"2026-11-08T18:00Z"}
    saved=dict(store)
    health={"generated_at_utc":(now-timedelta(minutes=10)).isoformat(),
            "agents":{f"ACS-{i:02d}":{"verified":True,"status":"current",
                         "health_status":"healthy"} for i in range(1,6)}}
    mutations=[]
    def fake(url,token=None,method="GET",body=None):
        if url==g.REPORT_URL:
            if method!="GET":raise AssertionError("report_write")
            return dict(health)
        if url!=g.API_URL or token!="dummy-token":
            raise AssertionError("unexpected_endpoint")
        if method=="PATCH":
            if body not in ({"enabled":True},{"enabled":False}):
                raise AssertionError("unauthorized_patch")
            mutations.append(dict(body))
            store.update(body)
            store["next_run"]="2026-11-09T18:00Z"
        return dict(store)
    result=controlled_probe("dummy-token",fake,now)
    if result["status"]!="GITHUB_INITIATED_SCHEDULE_REENABLE_VERIFIED":
        raise RuntimeError("simulation_controller_failed")
    if not result["restoration_verified"] or not store["enabled"]:
        raise RuntimeError("simulation_restore_failed")
    if not g.task_configuration_diff(saved,store)["safe"]:
        raise RuntimeError("simulation_drift")
    if mutations!=[{"enabled":False},{"enabled":True}]:
        raise RuntimeError("unexpected_simulated_mutations")
    info.update({"status":"ISOLATED_SIMULATION_PASS",
                 "mutations_simulated":len(mutations),
                 "production_changed":False,
                 "restoration_verified":True})
    return info

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    info=snapshot()
    if not args.execute:
        info=simulated_probe()
        report(info["status"],info)
        print(json.dumps(info,sort_keys=True))
        return 0
    reason=test_preflight(os.environ,datetime.now(UTC))
    if reason:
        info["status"]="BLOCKED_"+reason
        report(info["status"],info)
        print(json.dumps(info,sort_keys=True))
        return 2
    def on_term(signum,frame):
        raise KeyboardInterrupt("termination_requested_restore")
    signal.signal(signal.SIGTERM,on_term)
    signal.signal(signal.SIGINT,on_term)
    try:
        info=controlled_probe(os.environ["PYTHONANYWHERE_API_TOKEN"])
    except BaseException as exc:
        # Do not show token, endpoint body, or traceback contents.
        info["status"]="CRITICAL_or_FAILED_probe_exception"
        info["error_type"]=type(exc).__name__
        # restore_if_needed runs in controlled_probe's finally if disable attempted.
        # If restore also throws, it cannot be certified; human check required.
    report(info["status"],info)
    print(json.dumps(info,sort_keys=True))
    return 0 if info["status"]=="GITHUB_INITIATED_SCHEDULE_REENABLE_VERIFIED" and info["restoration_verified"] else 2

if __name__=="__main__":
    sys.exit(main())
