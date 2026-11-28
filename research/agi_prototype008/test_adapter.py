import unittest,tempfile,json
from adapter import Adapter,ScriptedProvider,TemporaryProviderError,verify
D='2026-12-01T12:00:00+00:00'
def msg(*g): return json.dumps({'version':1,'goals':g})
class AdapterTests(unittest.TestCase):
 def run_case(self,replies,scope=('bill_tracking',),permissions=('bills',),fixtures=None):
  with tempfile.TemporaryDirectory() as tmp:
   p=ScriptedProvider(replies); a=Adapter(tmp,p)
   try: r=a.run('fictional objective',scope,permissions,'one',D,{'bills':[]} if fixtures is None else fixtures,D); return r,p.calls
   finally:a.close()
 def test_valid(self):
  r,n=self.run_case([msg('bill_tracking')]);self.assertEqual(r['status'],'procedure_verified');self.assertFalse(r['objectives_confirmed']);self.assertEqual(n,1)
 def test_composed(self):
  r,n=self.run_case([msg('bill_tracking','appointment_tracking')],('bill_tracking','appointment_tracking'),('bills','calendar'),{'bills':[],'calendar':[]});self.assertEqual(r['status'],'procedure_verified')
 def test_retry(self):self.assertEqual(self.run_case([TemporaryProviderError(),msg('bill_tracking')])[1],2)
 def test_malformed_retry(self):self.assertEqual(self.run_case(['not json',msg('bill_tracking')])[0]['status'],'procedure_verified')
 def test_exhausted(self):
  r,n=self.run_case(['bad','bad',msg('bill_tracking')]);self.assertEqual(n,2);self.assertFalse(r['executed'])
 def test_scope(self):self.assertEqual(self.run_case([msg('appointment_tracking')],permissions=('calendar','bills'))[0]['status'],'denied')
 def test_permission(self):self.assertFalse(self.run_case([msg('bill_tracking')],permissions=())[0]['executed'])
 def test_extra_field(self):self.assertFalse(self.run_case(['{"version":1,"goals":["bill_tracking"],"send":true}']*2)[0]['executed'])
 def test_duplicate_field(self):self.assertFalse(self.run_case(['{"version":1,"version":1,"goals":["bill_tracking"]}']*2)[0]['executed'])
 def test_unknown_goal(self):self.assertFalse(self.run_case([msg('send_email')]*2)[0]['executed'])
 def test_size(self):self.assertFalse(self.run_case([' '*4097]*2)[0]['executed'])
 def test_boolean_version(self):self.assertFalse(self.run_case(['{"version":true,"goals":["bill_tracking"]}']*2)[0]['executed'])
 def test_missing_fixture(self):self.assertEqual(self.run_case([msg('bill_tracking')],fixtures={})[0]['status'],'incomplete')
 def test_forged_completion(self):self.assertFalse(self.run_case([msg('bill_tracking')],fixtures={'bills':[],'payment_confirmation':True})[0]['objectives_confirmed'])
 def test_independent_plan_check(self):
  with self.assertRaises(PermissionError):verify(['bill_tracking'],['bill_tracking'],{'bills'},('briefing',))
