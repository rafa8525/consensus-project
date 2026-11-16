import unittest
from acs01_emergency_restore import TASK_ID, compare, inspect

BASE={"id":TASK_ID,"command":"bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh",
      "enabled":True,"interval":"daily","hour":10,"minute":0,"next_run":"2026-11-18T18:00Z"}

class SafetyTests(unittest.TestCase):
    def test_healthy_noop(self):
        calls=[]
        def api(**kw):
            calls.append(kw)
            return dict(BASE)
        self.assertEqual(inspect(BASE,api)["status"],"HEALTHY_NOOP")
        self.assertEqual(calls,[{}])
    def test_readonly_disabled(self):
        state=dict(BASE,enabled=False)
        self.assertEqual(inspect(BASE,lambda **kw:dict(state))["status"],
                         "DISABLED_RESTORE_AVAILABLE_NOT_EXECUTED")
    def test_enable_only_and_verify(self):
        state=dict(BASE,enabled=False)
        patch=[]
        def api(method="GET",payload=None):
            if method=="PATCH":
                self.assertEqual(payload,{"enabled":True})
                state.update(payload);patch.append(payload)
            return dict(state)
        self.assertEqual(inspect(BASE,api,restore=True,confirmed=True)["status"],
                         "RESTORED_ENABLED_NEXT_RUN_ONLY")
        self.assertEqual(len(patch),1)
    def test_maintenance_blocks(self):
        state=dict(BASE,enabled=False)
        self.assertEqual(inspect(BASE,lambda **kw:dict(state),restore=True,confirmed=True,
                                 maintenance=True)["status"],"BLOCKED_MAINTENANCE")
    def test_command_drift_blocks(self):
        state=dict(BASE,enabled=False,command="unexpected")
        self.assertEqual(inspect(BASE,lambda **kw:dict(state))["status"],"BLOCKED_CONFIGURATION_DRIFT")
    def test_extra_field_blocks(self):
        state=dict(BASE,enabled=False,unexpected=1)
        self.assertFalse(compare(BASE,state)[0])
    def test_volatile_timestamp_allowed(self):
        state=dict(BASE,enabled=False,next_run="2026-11-19T18:00Z")
        self.assertTrue(compare(BASE,state)[0])
    def test_changed_state_before_write_blocks(self):
        n=[0]
        def api(**kw):
            n[0]+=1
            return dict(BASE,enabled=n[0]!=1)
        self.assertEqual(inspect(BASE,api,restore=True,confirmed=True)["status"],
                         "BLOCKED_PREWRITE_STATE_CHANGED")
    def test_api_error_is_not_swallowed(self):
        def api(**kw):raise TimeoutError("isolated")
        with self.assertRaises(TimeoutError):
            inspect(BASE,api,restore=True,confirmed=True)
    def test_failed_postwrite_never_certifies(self):
        state=dict(BASE,enabled=False)
        self.assertEqual(inspect(BASE,lambda **kw:dict(state),restore=True,confirmed=True)["status"],
                         "CRITICAL_RESTORE_NOT_VERIFIED")

if __name__=="__main__":
    unittest.main()
