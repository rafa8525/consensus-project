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
    def test_explicit_maintenance_blocks_enable(self):
        f,c=mock(report(29),task(False))
        result=g.guard(True,True,"test-token",NOW,f,maintenance=True)
        self.assertEqual(result["status"],"BLOCKED_explicit_maintenance_mode")
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_unexpected_schedule_metadata_change_after_patch_escalates(self):
        state=task(False)
        calls=[]
        def fetch(url,token=None,method="GET",body=None):
            calls.append(method)
            if url==g.REPORT_URL: return report()
            if method=="PATCH":
                state.update(body)
                state["description"]="unexpected"
                return dict(state)
            return dict(state)
        result=g.guard(True,True,"test-token",NOW,fetch)
        self.assertEqual(result["status"],"ESCALATE_configuration_change")
        self.assertTrue(result["changed"])
        self.assertEqual(calls.count("PATCH"),1)
    def test_disabled_schedule_missing_or_invalid_report_blocks(self):
        f,c=mock({"generated_at_utc":"bad","agents":{}},task(False))
        result=g.guard(True,True,"test-token",NOW,f)
        self.assertTrue(result["status"].startswith("BLOCKED_"))
        self.assertFalse(any(x[0]=="PATCH" for x in c))
    def test_runtime_timestamp_changes_after_patch_are_allowed(self):
        state=task(False)
        state["next_run"]="2026-11-08T18:00Z"
        calls=[]
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            calls.append((method,body))
            if method=="PATCH":
                self.assertEqual(body,{"enabled":True})
                state["enabled"]=True
                state["next_run"]="2026-11-09T18:00Z"
            return dict(state)
        result=g.guard(True,True,"token",NOW,fetch)
        self.assertEqual(result["status"],"SCHEDULE_REENABLED_NEXT_RUN_ONLY")
        self.assertEqual(result["allowed_api_metadata_changes"],["next_run"])
        self.assertEqual([c for c in calls if c[0]=="PATCH"],[("PATCH",{"enabled":True})])
    def test_prewrite_timestamp_change_is_allowed(self):
        state=task(False)
        state["next_run"]="a"
        reads=[0]
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            if method=="GET":
                reads[0]+=1
                if reads[0]==2: state["next_run"]="b"
            elif method=="PATCH":
                self.assertEqual(body,{"enabled":True})
                state["enabled"]=True
            return dict(state)
        result=g.guard(True,True,"token",NOW,fetch)
        self.assertEqual(result["status"],"SCHEDULE_REENABLED_NEXT_RUN_ONLY")
    def test_unrecognized_field_change_after_patch_blocks(self):
        state=task(False)
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            if method=="PATCH":
                state["enabled"]=True
                state["new_api_field"]="unexpected"
            return dict(state)
        result=g.guard(True,True,"token",NOW,fetch)
        self.assertEqual(result["status"],"ESCALATE_configuration_change")
        self.assertEqual(result["changed_field_names"],["new_api_field"])
    def test_extra_field_before_patch_blocks(self):
        state=task(False)
        calls=[]
        seen=[0]
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            if method=="GET":
                seen[0]+=1
                if seen[0]==2: state["unexpected"]="value"
            else: calls.append((method,body))
            return dict(state)
        result=g.guard(True,True,"token",NOW,fetch)
        self.assertEqual(result["status"],"BLOCKED_prewrite_schedule_changed")
        self.assertEqual(calls,[])
    def test_timestamp_key_missing_blocks(self):
        before=task(False)
        before["next_run"]="timestamp"
        after=task(False)
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
    def test_integer_enabled_is_not_boolean(self):
        t=task(False);t["enabled"]=1
        self.assertEqual(g.validate_task(t),"invalid_enabled")
    def test_provider_can_enable_recalculation_after_enable_is_metadata(self):
        before=task(False);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        d=g.task_configuration_diff(before,after)
        self.assertTrue(d["safe"])
        self.assertEqual(d["api_metadata"],["can_enable"])

    def test_can_enable_mutation_without_transition_is_blocked(self):
        before=task(True);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])

    def test_can_enable_mutation_with_command_drift_is_blocked(self):
        before=task(False);before["can_enable"]=True
        after=task(True);after["can_enable"]=False
        after["command"]="unexpected"
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])

    def test_can_enable_field_addition_or_type_change_is_blocked(self):
        before=task(False)
        after=task(True);after["can_enable"]=False
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])
        before["can_enable"]=True
        after["can_enable"]="false"
        self.assertFalse(g.task_configuration_diff(before,after)["safe"])

    def test_guard_recovers_with_provider_capability_recalculation(self):
        state=task(False);state["can_enable"]=True
        writes=[]
        def fetch(url,token=None,method="GET",body=None):
            if url==g.REPORT_URL:return report()
            if method=="PATCH":
                writes.append(body)
                state["enabled"]=True
                state["can_enable"]=False
            return dict(state)
        result=g.guard(True,True,"token",NOW,fetch)
        self.assertEqual(result["status"],"SCHEDULE_REENABLED_NEXT_RUN_ONLY")
        self.assertEqual(result["allowed_api_metadata_changes"],["can_enable"])
        self.assertEqual(writes,[{"enabled":True}])

    def test_invalid_enabled_rejected(self):
        t=task();t["enabled"]="true"
        self.assertEqual(g.validate_task(t),"invalid_enabled")

if __name__=="__main__": unittest.main()
