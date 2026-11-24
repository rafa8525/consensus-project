import unittest,tempfile
from pathlib import Path
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
from integration import *
NOW=datetime(2026,11,24,tzinfo=timezone.utc)
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'synthetic.db'; Ledger.initialize(self.path)
    def reserve(self,l,i,units=1,product='gmail',now=NOW):
        return l.reserve('synthetic-project',product,units,now,f'synthetic-{i}')
    def test_restart_and_replay(self):
        self.assertTrue(self.reserve(Ledger(self.path,3),1,2))
        self.assertFalse(self.reserve(Ledger(self.path,3),1))
        self.assertTrue(self.reserve(Ledger(self.path,3),2))
        self.assertFalse(self.reserve(Ledger(self.path,3),3))
        self.assertTrue(self.reserve(Ledger(self.path,3),4,product='drive'))
    def test_concurrent_connections(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(lambda i:self.reserve(Ledger(self.path,10),i),range(50))),10)
    def test_missing_and_corrupt(self):
        p=Path(self.tmp.name)/'missing.db'; self.assertFalse(self.reserve(Ledger(p),1)); self.assertFalse(p.exists())
        p.write_text('synthetic invalid database'); self.assertFalse(self.reserve(Ledger(p),1))
    def test_invalid_units(self):
        for value in [True,0,-1,1.5,4501]: self.assertFalse(self.reserve(Ledger(self.path),1,value))
    def test_mock_failure_no_retry(self):
        m=MockMCP(Ledger(self.path,3)); opts=dict(tier='standard',route='google_mcp',authorized=True,active=True)
        self.assertEqual(m.invoke('AGI-01','gmail',2,NOW,'synthetic-call',fail=True,**opts),'uncertain_stop')
        self.assertEqual(m.invoke('AGI-01','gmail',2,NOW,'synthetic-call',**opts),'denied')
        self.assertEqual(m.invoke('AGI-01','gmail',2,NOW,'synthetic-other',**opts),'denied'); self.assertEqual(m.calls,1)
        for flag,val in [('tier','scaled'),('route','rest'),('authorized',False),('active',False)]:
            self.assertEqual(m.invoke('AGI-01','gmail',1,NOW,'synthetic-other',**(opts|{flag:val})),'denied')
    def test_all_roles_and_stores(self):
        m=MockMemory(); self.assertEqual(len(ROLES),55)
        for role in ROLES:
            for store in STORES:
                for source in SOURCES-{'independent'}:
                    r=Record(frozenset({source}),NOW,NOW+timedelta(days=1),'synthetic-grant',True)
                    self.assertFalse(m.put(role,store,'synthetic-item',r,NOW,durable=False))
                r=Record(frozenset({'independent'}),NOW,NOW+timedelta(days=1),'synthetic-grant',True)
                key='synthetic-'+role; self.assertTrue(m.put(role,store,key,r,NOW)); self.assertEqual(m.read(role,store,key,NOW),r)
        m.revoke('synthetic-grant'); self.assertEqual(len(m.pending_removal(NOW)),220)
        self.assertIsNone(m.read('AGI-01','GitHub','synthetic-AGI-01',NOW))
    def test_lineage_and_expiry(self):
        a=Record(frozenset({'independent'}),NOW,NOW+timedelta(days=40),'synthetic-g',True)
        b=Record(frozenset({'workspace_user'}),NOW-timedelta(days=29),NOW+timedelta(days=2),'synthetic-g',True)
        r=derive(a,b); self.assertEqual(r.acquired,b.acquired); self.assertEqual(r.deadline,b.deadline)
        m=MockMemory(); self.assertTrue(m.allowed('AGI-01',r,'process',NOW)); self.assertFalse(m.allowed('AGI-01',r,'train',NOW)); self.assertFalse(m.allowed('AGI-01',r,'evaluation_dataset',NOW)); self.assertFalse(m.allowed('AGI-01',r,'process',NOW+timedelta(days=1)))
        self.assertFalse(m.allowed('AGI-56',a,'process',NOW)); self.assertFalse(m.allowed('AGI-01',a,'process',a.deadline))
        with self.assertRaises(ValueError): derive(a,Record(b.sources,b.acquired,b.deadline,'synthetic-other'))
if __name__=='__main__': unittest.main()
