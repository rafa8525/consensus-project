#!/usr/bin/env python3
"""Mock-only tests for controlled scheduler intervention; no network writes."""
import unittest
import phase1_controlled_scheduler_test as target

COMMAND="bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh"
class Guard:
    API_URL="https://test.invalid/schedule/1524414/"
    REPORT_URL="https://test.invalid/report.json"
    def validate_task(self,task):
        return None if task.get("id")==1524414 and task.get("command")==COMMAND and type(task.get("enabled")) is bool else "invalid"
    def guard(self,apply,allowed,token,fetcher):
        item=fetcher(self.API_URL,token=token)
        if item["enabled"] is False:
            fetcher(self.API_URL,token=token,method="PATCH",body={"enabled":True})
            return {"status":"SCHEDULE_REENABLED_NEXT_RUN_ONLY"}
        return {"status":"HEALTHY_NOOP"}

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.g=Guard()
        self.state={"id":1524414,"command":COMMAND,"enabled":True,"interval":"daily","hour":10,"minute":0}
        self.changes=[]
    def api(self,url,token=None,method="GET",body=None):
        if method=="PATCH":
            self.changes.append(dict(body))
            self.state.update(body)
        return dict(self.state)
    def test_simulation_performs_no_real_write(self):
        r=target.test(self.g,self.api,"token",False)
        self.assertTrue(r["passed"])
        self.assertEqual(self.changes,[])
        self.assertTrue(self.state["enabled"])
    def test_mismatched_task_blocks(self):
        self.state["id"]=12
        with self.assertRaises(RuntimeError):
            target.test(self.g,self.api,"token",False)
        self.assertEqual(self.changes,[])
    def test_configuration_equality(self):
        before=dict(self.state)
        after={**before,"enabled":False}
        self.assertTrue(target.same_config(before,after))
        after["hour"]=11
        self.assertFalse(target.same_config(before,after))

if __name__=="__main__":
    unittest.main()
