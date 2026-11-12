"""Durable Phase 5 replay and recovery tests with synthetic handlers."""
import os
import subprocess
import sys
import tempfile
import unittest
from agents.phase5_durable import DurableMockRegistry
from agents.phase2_protocol import ProtocolError

class DurableRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=os.path.join(self.temp.name,"events.sqlite")
        self.calls=[]
    def tearDown(self): self.temp.cleanup()
    def make(self, handler=None):
        reg=DurableMockRegistry(self.db,simulation=True)
        reg.register(adapter_id="test.mock",capability="bills",
            workflow_key="existing.alert",owner="acs-02",
            permissions={"notify_mock"},handler=handler or (lambda p:self.calls.append(p) or "ok"))
        return reg
    def send(self,reg,**kwargs):
        data=dict(adapter_id="test.mock",principal="acs-02",
                  permission="notify_mock",event_id="evt1",
                  payload={"synthetic_value":"sample"})
        data.update(kwargs)
        return reg.dispatch(**data)
    def test_duplicate_blocked_after_restart(self):
        a=self.make();self.assertEqual(self.send(a)["status"],"delivered");a.close()
        b=self.make();r=self.send(b)
        self.assertEqual(r["status"],"delivered")
        self.assertTrue(r["duplicate"]);self.assertFalse(r["executed"])
        self.assertEqual(len(self.calls),1);b.close()
    def test_collision_after_restart(self):
        a=self.make();self.send(a);a.close()
        b=self.make()
        with self.assertRaises(ProtocolError):
            self.send(b,payload={"synthetic_value":"other"})
        b.close()
    def test_failure_not_retried(self):
        calls=[]
        def fail(p): calls.append(p);raise RuntimeError("private")
        a=self.make(fail)
        self.assertEqual(self.send(a)["status"],"uncertain");a.close()
        b=self.make(fail)
        self.assertEqual(self.send(b)["status"],"uncertain")
        self.assertEqual(len(calls),1);b.close()
    def test_actual_process_exit_after_durable_claim(self):
        # External child deliberately terminates inside the mock handler.
        src=(
          "import os,sys\n"
          "from agents.phase5_durable import DurableMockRegistry\n"
          "r=DurableMockRegistry(sys.argv[1],simulation=True)\n"
          "r.register(adapter_id='test.mock',capability='bills',workflow_key='existing.alert',"
          "owner='acs-02',permissions={'notify_mock'},handler=lambda p:os._exit(41))\n"
          "r.dispatch(adapter_id='test.mock',principal='acs-02',permission='notify_mock',"
          "event_id='evt1',payload={'synthetic_value':'sample'})\n"
        )
        proc=subprocess.run([sys.executable,"-c",src,self.db],
                            capture_output=True,text=True,timeout=15)
        self.assertEqual(proc.returncode,41,proc.stderr)
        b=self.make()
        r=self.send(b)
        self.assertEqual(r["status"],"claimed")
        self.assertTrue(r["duplicate"]);self.assertFalse(r["executed"])
        self.assertEqual(self.calls,[]);b.close()
    def test_no_permission_bypass_on_duplicate(self):
        a=self.make();self.send(a);a.close()
        b=self.make()
        with self.assertRaises(ProtocolError):
            self.send(b,principal="acs-03")
        b.close()
    def test_simulation_required(self):
        with self.assertRaises(ProtocolError): DurableMockRegistry(self.db)

if __name__=="__main__": unittest.main()
