import sqlite3,tempfile,unittest
from pathlib import Path
from leased_worker import connect,setup,enqueue,claim,heartbeat,complete,reclaim_expired,model_job,status
RESULT={'production_changed':False,'model_trained_in_this_task':False,'ok':True}
class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'queue.sqlite';self.c=connect(self.db)
        self.addCleanup(self.c.close);setup(self.c)
    def add(self,tid='a'): enqueue(self.c,tid,'AGI-01','design_experiment','Design baseline')
    def test_claim_complete(self):
        self.add();r=claim(self.c,'AGI-01',now=100)
        self.assertTrue(complete(self.c,r,RESULT,now=101))
        self.assertEqual(status(self.c)[0]['status'],'done')
    def test_claim_exclusive(self):
        self.add();claim(self.c,'AGI-01',now=100)
        self.assertIsNone(claim(self.c,'AGI-01',now=101))
    def test_heartbeat(self):
        self.add();r=claim(self.c,'AGI-01',seconds=10,now=100)
        self.assertTrue(heartbeat(self.c,'a',r['token'],seconds=10,now=108))
        self.assertEqual(reclaim_expired(self.c,now=115),0)
        self.assertTrue(complete(self.c,r,RESULT,now=116))
    def test_recovery_fencing(self):
        self.add();old=claim(self.c,'AGI-01',seconds=5,now=100)
        self.assertEqual(reclaim_expired(self.c,now=106),1)
        new=claim(self.c,'AGI-01',seconds=5,now=107)
        self.assertNotEqual(old['token'],new['token'])
        self.assertFalse(complete(self.c,old,RESULT,now=108))
        self.assertTrue(complete(self.c,new,RESULT,now=108))
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM lease_events WHERE kind='completed'").fetchone()[0],1)
    def test_retry_limit(self):
        self.add();claim(self.c,'AGI-01',seconds=5,now=100)
        reclaim_expired(self.c,now=106);claim(self.c,'AGI-01',seconds=5,now=107)
        reclaim_expired(self.c,now=113)
        self.assertEqual(status(self.c)[0]['status'],'failed')
        self.assertEqual(status(self.c)[0]['attempts'],2)
    def test_expired_heartbeat(self):
        self.add();r=claim(self.c,'AGI-01',seconds=5,now=100)
        self.assertFalse(heartbeat(self.c,'a',r['token'],now=106))
        self.assertFalse(complete(self.c,r,RESULT,now=106))
    def test_wrong_owner(self):
        self.add();r=claim(self.c,'AGI-01',now=100)
        self.assertFalse(complete(self.c,{**r,'token':'wrong'},RESULT,now=101))
        self.assertTrue(complete(self.c,r,RESULT,now=101))
    def test_unknown_agent(self):
        with self.assertRaises(ValueError): enqueue(self.c,'a','AGI-99','design_experiment','x')
    def test_disallowed_operation(self):
        with self.assertRaises(ValueError): enqueue(self.c,'a','AGI-01','shell','x')
    def test_duplicate(self):
        self.add()
        with self.assertRaises(sqlite3.IntegrityError): self.add()
    def test_contract(self):
        self.add();r=claim(self.c,'AGI-01',now=100)
        with self.assertRaises(ValueError): complete(self.c,r,{'production_changed':True,'model_trained_in_this_task':False},now=101)
    def test_persistence(self):
        self.add();r=claim(self.c,'AGI-01',now=100);complete(self.c,r,RESULT,now=101)
        other=connect(self.db)
        try: self.assertEqual(status(other)[0]['status'],'done')
        finally: other.close()
    def test_inference(self):
        self.add();r=claim(self.c,'AGI-01',now=100)
        predicted=model_job(r,{'model':{},'sha256':'test'},lambda model,text:{'label':'design_experiment'})
        self.assertTrue(complete(self.c,r,predicted,now=101))
    def test_capacity(self):
        for i in range(55): self.add(str(i))
        with self.assertRaises(ValueError): self.add('overflow')
if __name__=='__main__':unittest.main()
