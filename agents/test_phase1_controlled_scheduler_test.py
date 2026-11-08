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
        r=target.test(self.g,"token",False,self.api)
        self.assertTrue(r["passed"])
        self.assertEqual(self.changes,[])
        self.assertTrue(self.state["enabled"])
    def test_mismatched_task_blocks(self):
        self.state["id"]=12
        with self.assertRaises(RuntimeError):
            target.test(self.g,"token",False,self.api)
        self.assertEqual(self.changes,[])
    def test_real_guard_simulation_does_not_modify_api(self):
        from datetime import datetime, timezone
        import phase1_independent_schedule_guard as actual_guard
        calls=[]
        def fake_api(url, token=None, method="GET", body=None):
            if method!="GET":
                calls.append((method,body))
                raise AssertionError("live API mutation attempted in simulation")
            return dict(self.state)
        outcome=target.test(actual_guard,"test-token",False,fake_api)
        self.assertTrue(outcome["passed"])
        self.assertEqual(calls,[])
    def test_generated_next_run_timestamp_is_classified(self):
        before=dict(self.state, next_run='2026-11-08T18:00Z')
        after=dict(before, enabled=False, next_run='2026-11-09T18:00Z')
        result=target.classify_schedule_difference(before,after)
        self.assertTrue(result['safe_to_continue'])
        self.assertEqual(result['metadata_changed'],['next_run'])
        self.assertEqual(result['core_changed'],[])
    def test_changed_command_is_blocked_even_with_volatile_change(self):
        before=dict(self.state, next_run='one')
        after=dict(before, enabled=False, next_run='two', command='other.sh')
        result=target.classify_schedule_difference(before,after)
        self.assertFalse(result['safe_to_continue'])
        self.assertIn('command',result['core_changed'])
    def test_unrecognized_metadata_is_not_silently_whitelisted(self):
        before=dict(self.state)
        after=dict(before, enabled=False, mystery_field='new')
        result=target.classify_schedule_difference(before,after)
        self.assertFalse(result['safe_to_continue'])
        self.assertIn('mystery_field',result['unclassified_changed'])
    def test_removed_schedule_metadata_is_blocked(self):
        before=dict(self.state, extra='original')
        after=dict(self.state, enabled=False)
        result=target.classify_schedule_difference(before,after)
        self.assertFalse(result['safe_to_continue'])
        self.assertIn('extra',result['unclassified_changed'])
    def test_volatile_and_enabled_only_change_is_accepted(self):
        before=dict(self.state, updated_at='old')
        after=dict(before, enabled=False, updated_at='new')
        self.assertTrue(target.same_config(before,after))
    def test_configuration_equality(self):
        before=dict(self.state)
        after={**before,"enabled":False}
        self.assertTrue(target.same_config(before,after))
        after["hour"]=11
        self.assertFalse(target.same_config(before,after))

if __name__=="__main__":
    unittest.main()
