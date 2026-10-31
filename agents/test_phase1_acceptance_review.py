#!/usr/bin/env python3
"""Isolated regression checks; no network, Git changes or production execution."""
import copy
import unittest
from datetime import datetime, timedelta, timezone
import phase1_acceptance_review as gate

NOW = datetime(2026, 10, 31, 18, 3, tzinfo=timezone.utc)
def iso(time):
    return time.isoformat()
def fixture():
    return {
        "generated_at_utc": iso(NOW),
        "agents": {n: {"status":"current", "verified":True,
                        "health_status":"healthy", "last_execution_utc":iso(NOW)}
                   for n in gate.AGENTS},
        "pythonanywhere_schedule":{"available":True,"acs01_task":{"enabled":True},
                                   "health_task":{"enabled":False}},
        "git":{"origin_reachable":{"ok":True}, "unresolved_merge_conflict":False,
               "status":{"tracked_changes_count":22}},
        "self_heal":{"branch_sync":{"ok":True,"ahead_after":0,"behind_after":0}}
    }
def proof():
    return {"tests":{k:{"passed":True, "source":"reviewed-test-log",
                         "executed_at_utc":iso(NOW)}
                     for k in ("failure_detection", "automatic_retry",
                               "recovery_verified", "bounded_escalation")}}
class Tests(unittest.TestCase):
    def test_healthy_parent_architecture(self):
        self.assertTrue(all(gate.evaluate(fixture(), proof(), NOW).values()))
    def test_each_agent_unhealthy(self):
        for n in gate.AGENTS:
            for field,value in (("verified",False),("status","stale"),
                                ("last_execution_utc","2020-01-01T00:00:00+00:00")):
                r=fixture()
                r["agents"][n][field]=value
                self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_malformed_agent_data(self):
        for malformed in (None, [], "bad", 1):
            r=fixture()
            r["agents"]["ACS-04"]=malformed
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_missing_proof(self):
        for k in proof()["tests"]:
            p=proof()
            del p["tests"][k]
            self.assertFalse(all(gate.evaluate(fixture(), p, NOW).values()))
    def test_old_and_future_report(self):
        for t in (NOW-timedelta(days=3), NOW+timedelta(seconds=1)):
            r=fixture()
            r["generated_at_utc"]=iso(t)
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_scheduler_and_remote_sync(self):
        for field in ("scheduler", "sync", "remote"):
            r=fixture()
            if field=="scheduler":r["pythonanywhere_schedule"]["acs01_task"]["enabled"]=False
            if field=="sync":r["self_heal"]["branch_sync"]["behind_after"]=1
            if field=="remote":r["git"]["origin_reachable"]["ok"]=False
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_unique_cycle_and_replay(self):
        history={}
        for i in range(3):
            t=NOW+timedelta(days=i)
            r=fixture()
            r["generated_at_utc"]=iso(t)
            r["agents"]={n:{**a,"last_execution_utc":iso(t)} for n,a in r["agents"].items()}
            p=proof()
            checks,cycles,completed=gate.advance(r,p,history,t)
            self.assertEqual(len(cycles),i+1)
            self.assertEqual(completed,i==2)
            history={"passing_reports":cycles}
        checks,cycles,completed=gate.advance(r,p,history,t)
        self.assertEqual(len(cycles),3)
        self.assertTrue(completed)
        r["agents"]["ACS-02"]["verified"]=False
        _,cycles,completed=gate.advance(r,p,history,t)
        self.assertEqual(cycles,[])
        self.assertFalse(completed)

if __name__=="__main__":
    unittest.main()
