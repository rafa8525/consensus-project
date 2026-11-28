import tempfile,unittest
from planner import Planner
D='2026-12-01T12:00:00+00:00'
class Test(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory();self.p=Planner(self.tmp.name)
 def tearDown(self):self.p.close();self.tmp.cleanup()
 def test_compose(self):self.assertEqual(self.p.plan(['bill_tracking','appointment_tracking'],['bills','calendar'])[1],('appointment','bill'))
 def test_permission(self):
  with self.assertRaises(PermissionError):self.p.plan(['overview'],['calendar'])
 def test_unknown(self):
  with self.assertRaises(ValueError):self.p.plan(['send_email'],['calendar'])
 def test_reuse(self):
  args=(['bill_tracking','appointment_tracking'],['bills','calendar'],'one',D,{'bills':[],'calendar':[]},D)
  r=self.p.run(*args);self.assertTrue(r['procedure_verified']);self.assertFalse(r['objectives_confirmed']);self.assertFalse(r['reused']);self.p.close();self.p=Planner(self.tmp.name);self.assertTrue(self.p.run(*args)['reused'])
 def test_failed_not_cached(self):
  r=self.p.run(['bill_tracking'],['bills'],'one',D,{},D);self.assertFalse(r['procedure_verified']);self.assertFalse(self.p.plan(['bill_tracking'],['bills'])[2])
 def test_no_forged_confirmation(self):
  r=self.p.run(['bill_tracking'],['bills'],'one',D,{'bills':[],'payment_confirmation':True},D);self.assertFalse(r['objectives_confirmed'])
 def test_tamper(self):
  k,_,_=self.p.plan(['bill_tracking'],['bills']);self.p.db.execute('INSERT INTO recipes VALUES(?,?,1)',(k,'["briefing"]'));self.p.db.commit()
  with self.assertRaises(ValueError):self.p.plan(['bill_tracking'],['bills'])
if __name__=='__main__':unittest.main()
