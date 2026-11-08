#!/usr/bin/env python3
"""Fully mocked CI regression for manual GitHub recovery exercise."""
import unittest
from datetime import datetime, timezone, timedelta
import phase1_github_controlled_probe as p
import phase1_independent_schedule_guard as g

NOW=datetime(2026,11,8,3,15,tzinfo=timezone.utc)
CMD="bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh"
REPORT={"generated_at_utc":(NOW-timedelta(minutes=10)).isoformat(),
        "agents":{f"ACS-{i:02d}":{"verified":True,"status":"current",
                    "health_status":"healthy"} for i in range(1,6)}}
class Fake:
    def __init__(self, fail_reenable=False, drift=False, fail_disable=False):
        self.task={"id":g.TASK_ID,"command":CMD,"enabled":True,
                   "interval":"daily","hour":10,"minute":0,"next_run":"old"}
        self.mutations=[]
        self.fail_reenable=fail_reenable
        self.fail_disable=fail_disable
        self.drift=drift
        self.fail_once=True
    def fetch(self,url,token=None,method="GET",body=None):
        if url==g.REPORT_URL:return dict(REPORT)
        if url!=g.API_URL:raise AssertionError("unexpected endpoint")
        if method=="PATCH":
            self.mutations.append(dict(body))
            if body=={"enabled":False} and self.fail_disable:
                raise OSError("fault while disabling")
            if body=={"enabled":True} and self.fail_reenable and self.fail_once:
                self.fail_once=False
                raise OSError("fault during recovery")
            self.task.update(body)
            self.task["next_run"]="new"
            if self.drift and body=={"enabled":False}:self.task["hour"]=11
        return dict(self.task)

class Tests(unittest.TestCase):
    def test_no_change_simulation(self):
        r=p.simulated_probe()
        self.assertEqual(r["status"],"ISOLATED_SIMULATION_PASS")
        self.assertFalse(r["production_changed"])
    def test_live_automated_recovery_on_fake_api(self):
        api=Fake()
        result=p.controlled_probe("fake",api.fetch,NOW)
        self.assertEqual(result["status"],"GITHUB_INITIATED_SCHEDULE_REENABLE_VERIFIED")
        self.assertTrue(result["restoration_verified"])
        self.assertEqual(api.mutations,[{"enabled":False},{"enabled":True}])
        self.assertTrue(api.task["enabled"])
    def test_one_recovery_api_failure_has_emergency_restore(self):
        api=Fake(fail_reenable=True)
        with self.assertRaises(OSError):
            p.controlled_probe("fake",api.fetch,NOW)
        self.assertTrue(api.task["enabled"])
        self.assertEqual(api.task["hour"],10)
        self.assertEqual(api.mutations,[{"enabled":False},{"enabled":True},{"enabled":True}])
    def test_bad_configuration_after_disable_restores_and_fails(self):
        api=Fake(drift=True)
        with self.assertRaises(RuntimeError):
            p.controlled_probe("fake",api.fetch,NOW)
        self.assertTrue(api.task["enabled"])
        self.assertNotEqual(api.task["hour"],10)
    def test_disable_api_failure_does_not_leave_disabled(self):
        api=Fake(fail_disable=True)
        with self.assertRaises(OSError):
            p.controlled_probe("fake",api.fetch,NOW)
        self.assertTrue(api.task["enabled"])
    def test_unexpected_main_dispatch_blocked(self):
        base={"GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":"refs/heads/main",
              "GITHUB_REPOSITORY":"rafa8525/consensus-project",
              "ACS_LIVE_TEST_CONFIRM":p.CONFIRM,
              "PYTHONANYWHERE_API_TOKEN":"fake"}
        self.assertIsNone(p.test_preflight(base,NOW))
        for k,v in (("GITHUB_REF","refs/heads/other"),
                    ("GITHUB_EVENT_NAME","push"),
                    ("GITHUB_REPOSITORY","other/repo"),
                    ("ACS_LIVE_TEST_CONFIRM","test"),
                    ("ACS_SCHEDULER_MAINTENANCE","true"),
                    ("ACS_SCHEDULER_RECOVERY_ENABLED","true")):
            modified=dict(base,**{k:v})
            self.assertIsNotNone(p.test_preflight(modified,NOW))
    def test_blocks_near_scheduled_task(self):
        self.assertFalse(p.eligible_utc(NOW.replace(hour=17,minute=50)))
        self.assertFalse(p.eligible_utc(NOW.replace(hour=18,minute=10)))
        self.assertTrue(p.eligible_utc(NOW))
if __name__=="__main__":
    unittest.main(verbosity=2)
