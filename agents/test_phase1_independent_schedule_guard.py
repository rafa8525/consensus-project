#!/usr/bin/env python3
"""Isolated PythonAnywhere schedule recovery tests; no real API calls."""
import copy
import unittest
from datetime import datetime, timezone, timedelta
import phase1_independent_schedule_guard as g

NOW=datetime(2026,11,8,2,tzinfo=timezone.utc)

def report(hours=1,healthy=True):
    agents={f"ACS-{n:02d}":{"verified":True,"status":"current","health_status":"healthy"} for n in range(1,6)}
    if not healthy: agents["ACS-02"]["verified"]=False
    return {"generated_at_utc":(NOW-timedelta(hours=hours)).isoformat(),"agents":agents}

def task(enabled=True):
    return {"id":1524414,"command":"bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
            "enabled":enabled,"interval":"daily","hour":10,"minute":0}

def mock(report_data,task_data,change=None,fail_patch=False):
    calls=[]
    state=copy.deepcopy(task_data)
    def fetch(url,token=None,method="GET",body=None):
        calls.append((method,url,body))
        if url==g.REPORT_URL:return report_data
        if method=="PATCH":
            if fail_patch:raise OSError("injected API failure")
            state.update(body)
            return copy.deepcopy(state)
        if change and len([x for x in calls if x[1]==g.API_URL])==2:
            state.update(change)
        return copy.deepcopy(state)
    return fetch,calls

class GuardTests(unittest.TestCase):
    def evaluate(self, r=None, t=None, apply=True, allow=True, change=None):
        f,c=mock(r if r is not None else report(),t if t is not None else task(),change)
        return g.guard(apply,allow,"test-token",NOW,f),c
    def test_healthy_noop(self):
        result,c=self.evaluate()
        self.assertEqual(result["status"],"HEALTHY_NOOP")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_stale_enabled_escalates(self):
        result,c=self.evaluate(r=report(29))
        self.assertEqual(result["status"],"ESCALATE_ENABLED_BUT_stale_report")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_unhealthy_enabled_escalates(self):
        result,_=self.evaluate(r=report(1,False))
        self.assertEqual(result["status"],"ESCALATE_ENABLED_BUT_unhealthy_agents")
    def test_disabled_dryrun(self):
        result,c=self.evaluate(r=report(29),t=task(False),apply=False)
        self.assertEqual(result["status"],"ENABLE_DISABLED_TASK")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_disabled_requires_explicit_permission(self):
        result,c=self.evaluate(t=task(False),allow=False)
        self.assertEqual(result["status"],"BLOCKED_apply_requires_allow_enable")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_disabled_reenabled_with_only_flag_patch(self):
        result,c=self.evaluate(t=task(False))
        self.assertEqual(result["status"],"SCHEDULE_REENABLED_NEXT_RUN_ONLY")
        self.assertEqual([x[2] for x in c if x[0]=="PATCH"],[{"enabled":True}])
    def test_live_can_enable_transition_is_metadata(self):
        before=task(False);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        diff=g.task_configuration_diff(before,after)
        self.assertTrue(diff["safe"])
        self.assertEqual(diff["api_metadata"],["can_enable"])
    def test_can_enable_type_change_is_not_metadata(self):
        before=task(False);before["can_enable"]=True
        after=task(True);after["can_enable"]="false"
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
    def test_can_enable_change_without_reenable_is_not_metadata(self):
        before=task(True);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
    def test_can_enable_change_with_command_drift_blocks(self):
        before=task(False);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        after["command"]="unexpected"
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
    def test_can_enable_field_added_blocks(self):
        before=task(False)
        after=task(True);after["can_enable"]=False
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
    def test_guard_recovers_with_can_enable_transition(self):
        state=task(False);state["can_enable"]=True
        calls=[]
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            if method=="PATCH":
                self.assertEqual(body,{"enabled":True})
                calls.append(body)
                state["enabled"]=True
                state["can_enable"]=False
            return copy.deepcopy(state)
        result=g.guard(True,True,"test-token",NOW,fetch)
        self.assertEqual(result["status"],"SCHEDULE_REENABLED_NEXT_RUN_ONLY")
        self.assertEqual(result["allowed_api_metadata_changes"],["can_enable"])
        self.assertEqual(len(calls),1)
    def test_wrong_command_blocks(self):
        t=task(False);t["command"]="malicious changed command"
        result,c=self.evaluate(t=t)
        self.assertEqual(result["status"],"BLOCKED_unexpected_command")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_wrong_id_blocks(self):
        t=task(False);t["id"]=9876
        result,c=self.evaluate(t=t)
        self.assertEqual(result["status"],"BLOCKED_unexpected_task_id")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_prewrite_changed_command_blocks(self):
        result,c=self.evaluate(t=task(False),change={"command":"changed"})
        self.assertEqual(result["status"],"BLOCKED_prewrite_schedule_changed")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_future_dated_blocks(self):
        result,_=self.evaluate(r=report(-1),t=task(False))
        self.assertEqual(result["status"],"BLOCKED_future_dated_report")
    def test_missing_agents_blocks(self):
        result,_=self.evaluate(r={"generated_at_utc":NOW.isoformat()},t=task(False))
        self.assertEqual(result["status"],"BLOCKED_missing_agents")
    def test_missing_token_blocks(self):
        f,c=mock(report(),task(False))
        self.assertEqual(g.guard(True,True,None,NOW,f)["status"],"BLOCKED_missing_api_token")
        self.assertEqual(c,[])
    def test_api_error_cannot_claim_success(self):
        f,c=mock(report(29),task(False),fail_patch=True)
        with self.assertRaises(OSError):g.guard(True,True,"token",NOW,f)
    def test_stale_threshold(self):
        self.assertEqual(g.inspect_report(report(28),NOW),"stale_report")
        self.assertEqual(g.inspect_report(report(1),NOW),"healthy")
    def test_invalid_enabled_rejected(self):
        t=task();t["enabled"]="true"
        self.assertEqual(g.validate_task(t),"invalid_enabled")

if __name__=="__main__": unittest.main()
