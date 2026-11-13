#!/usr/bin/env python3
"""End-to-end simulated disabled-scheduler recovery using the REAL guard.

All PythonAnywhere and report requests are replaced by an in-memory API.
No network traffic and no production schedule writes are possible.
"""
import json
import unittest
from datetime import datetime, timezone, timedelta
import phase1_independent_schedule_guard as guard

CLOCK=datetime(2026,11,8,3,15,tzinfo=timezone.utc)
TASK={'id':guard.TASK_ID,
      'command':'bash /home/rafa1215/consensus-project/agents/run_acs01_supervisor.sh',
      'enabled':True,'interval':'daily','hour':10,'minute':0}
REPORT={'generated_at_utc':(CLOCK-timedelta(minutes=15)).isoformat(),
        'agents':{f'ACS-{i:02d}':{'verified':True,'status':'current','health_status':'healthy'}
                  for i in range(1,6)}}

class FakeService:
    def __init__(self, disabled=False, fail_patch=False, drift=False):
        self.task=dict(TASK,enabled=not disabled)
        self.calls=[]
        self.fail_patch=fail_patch
        self.drift=drift
    def fetch(self,url,token=None,method='GET',body=None):
        if url==guard.REPORT_URL:
            if method!='GET' or token is not None:raise AssertionError('unexpected report request')
            return dict(REPORT)
        if url!=guard.API_URL or token!='fixture-only-token':
            raise AssertionError('unexpected API endpoint or token')
        self.calls.append({'method':method,'body':body})
        if method=='PATCH':
            if self.fail_patch:raise OSError('simulated PATCH outage')
            if body!={'enabled':True}:raise AssertionError('unauthorized mutation')
            self.task['enabled']=True
            if self.drift:self.task['command']='unapproved command'
        elif method!='GET':
            raise AssertionError('unexpected method')
        return dict(self.task)
    def writes(self):
        return [c for c in self.calls if c['method']!='GET']

class E2ETests(unittest.TestCase):
    def test_disabled_recovers_once_and_is_idempotent(self):
        api=FakeService(disabled=True)
        dry=guard.guard(False,False,'fixture-only-token',CLOCK,api.fetch)
        self.assertEqual(dry['status'],'ENABLE_DISABLED_TASK')
        self.assertEqual(api.writes(),[])
        fixed=guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch)
        self.assertEqual(fixed['status'],'SCHEDULE_REENABLED_NEXT_RUN_ONLY')
        self.assertTrue(fixed['changed'])
        self.assertTrue(api.task['enabled'])
        self.assertEqual(api.writes(),[{'method':'PATCH','body':{'enabled':True}}])
        again=guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch)
        self.assertEqual(again['status'],'HEALTHY_NOOP')
        self.assertEqual(len(api.writes()),1)
    def test_healthy_task_is_never_touched(self):
        api=FakeService()
        r=guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch)
        self.assertEqual(r['status'],'HEALTHY_NOOP')
        self.assertEqual(api.writes(),[])
    def test_maintenance_forbids_reenable(self):
        api=FakeService(disabled=True)
        r=guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch,maintenance=True)
        self.assertEqual(r['status'],'BLOCKED_explicit_maintenance_mode')
        self.assertEqual(api.writes(),[])
    def test_patch_network_failure_never_certifies(self):
        api=FakeService(disabled=True,fail_patch=True)
        with self.assertRaises(OSError):
            guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch)
        self.assertFalse(api.task['enabled'])
    def test_command_drift_after_patch_is_not_certified(self):
        api=FakeService(disabled=True,drift=True)
        r=guard.guard(True,True,'fixture-only-token',CLOCK,api.fetch)
        self.assertEqual(r['status'],'ESCALATE_postwrite_verification_failed')
        self.assertNotEqual(r['status'],'SCHEDULE_REENABLED_NEXT_RUN_ONLY')
    def test_enabled_stale_report_escalates_without_write(self):
        api=FakeService()
        stale=dict(REPORT,generated_at_utc=(CLOCK-timedelta(hours=40)).isoformat())
        original=api.fetch
        def fetch(url,token=None,method='GET',body=None):
            if url==guard.REPORT_URL:return stale
            return original(url,token,method,body)
        r=guard.guard(True,True,'fixture-only-token',CLOCK,fetch)
        self.assertEqual(r['status'],'ESCALATE_ENABLED_BUT_stale_report')
        self.assertEqual(api.writes(),[])

if __name__=='__main__':
    unittest.main(verbosity=2)
