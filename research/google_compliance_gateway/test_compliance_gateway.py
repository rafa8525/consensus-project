import unittest
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from compliance_gateway import ROLES, RESTRICTED, LEARNING, decide, Quota

NOW = datetime(2026, 11, 24, tzinfo=timezone.utc)
OLD = NOW - timedelta(days=1)

def check(role='AGI-01', sources=None, action='process', **kw):
    args = dict(authorized=True, active=True, connected=True, rights=True, task_deadline=NOW+timedelta(days=2))
    args.update(kw)
    now = args.pop('now', NOW)
    acquired = args.pop('acquired', OLD)
    return decide(role, {'independent'} if sources is None else sources, action, now, acquired, **args)[0]

class Tests(unittest.TestCase):
    def test_all_roles(self):
        self.assertEqual(len(ROLES), 55)
        for role in ROLES:
            with self.subTest(role=role):
                self.assertTrue(check(role, action='durable_memory'))
                for source in RESTRICTED:
                    self.assertTrue(check(role, {source}, 'process'))
                    for action in LEARNING | {'durable_memory'}:
                        self.assertFalse(check(role, {source, 'independent'}, action))
                    self.assertFalse(check(role, {source}, connected=False))
                    self.assertFalse(check(role, {source}, acquired=NOW-timedelta(days=30)))
                    self.assertFalse(check(role, {source}, task_deadline=NOW))
    def test_unknown(self):
        for sources in [set(), {'unknown'}, {'independent','unknown'}, ['independent']]:
            self.assertFalse(check(sources=sources))
        self.assertFalse(check(role='AGI-56'))
        self.assertFalse(check(action='export'))
    def test_authority(self):
        for flag in ['authorized','active','rights']:
            self.assertFalse(check(**{flag:False}))
        self.assertFalse(check(sources={'cloud_customer'}))
    def test_timestamps(self):
        self.assertFalse(check(now=NOW.replace(tzinfo=None)))
        self.assertFalse(check(acquired=NOW+timedelta(seconds=1)))
        self.assertFalse(check(sources={'workspace_user'}, task_deadline=None))
    def test_quota(self):
        q=Quota(3)
        def reserve(units=1, product='gmail', project='synthetic', day=NOW, **kw):
            opts=dict(tier='standard',route='google_mcp',verified=True,authorized=True)
            opts.update(kw)
            return q.reserve(project,product,units,day,**opts)
        for kw in [dict(tier='scaled'),dict(route='rest'),dict(verified=False),dict(authorized=False),dict(units=True),dict(units=0),dict(units=-1),dict(product='unknown'),dict(project=''),dict(day=NOW.replace(tzinfo=None))]:
            self.assertFalse(reserve(**kw))
        self.assertTrue(reserve(3)); self.assertFalse(reserve())
        self.assertTrue(reserve(product='drive')); self.assertTrue(reserve(project='other'))
        self.assertTrue(reserve(day=NOW+timedelta(days=1)))
    def test_concurrent_quota(self):
        q=Quota(10)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda _:q.reserve('synthetic','gmail',1,NOW,tier='standard',route='google_mcp',verified=True,authorized=True),range(100)))
        self.assertEqual(sum(results),10)
    def test_cap(self):
        for cap in [0,5001,True,1.5]:
            with self.assertRaises(ValueError): Quota(cap)

if __name__=='__main__': unittest.main()
