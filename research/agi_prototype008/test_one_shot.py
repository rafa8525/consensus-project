import unittest,tempfile,pathlib,json
from one_shot import execute
E=dict(GITHUB_EVENT_NAME='workflow_dispatch',GITHUB_REPOSITORY='rafa8525/consensus-project',GITHUB_REF='refs/heads/research/agi-iteration-001-20261119',GITHUB_RUN_ATTEMPT='1',AGI_APPROVAL='YES-PROTOTYPE-008',AGI_FINANCIAL_VERIFICATION='VERIFIED',AGI_ALLOWED_MODEL='gpt-5-mini',GITHUB_RUN_ID='123',AGI_AUTHORIZED_RUN_ID='123',OPENAI_API_KEY='fake',OPENAI_PROJECT_ID='fake')
class Tests(unittest.TestCase):
 def setUp(self):
  self.d=tempfile.TemporaryDirectory(); self.addCleanup(self.d.cleanup); self.marker=pathlib.Path(self.d.name)/'used'; self.n=0
 def send(self,b,e):
  self.n+=1; self.assertEqual(b['max_output_tokens'],512); self.assertNotIn('tools',b); return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'version':1,'goals':['bill_tracking','appointment_tracking']})}]}]}
 def test_success(self): self.assertEqual(execute(E,self.marker,self.send)['status'],'plan_validated'); self.assertEqual(self.n,1)
 def test_repeat(self):
  execute(E,self.marker,self.send)
  with self.assertRaises(FileExistsError): execute(E,self.marker,self.send)
  self.assertEqual(self.n,1)
 def test_gates(self):
  for k in E:
   with self.subTest(k=k),self.assertRaises(PermissionError): execute(dict(E,**{k:''}),self.marker,self.send)
  self.assertEqual(self.n,0)
 def test_wrong_run(self):
  with self.assertRaises(PermissionError): execute(dict(E,GITHUB_RUN_ID='124'),self.marker,self.send)
 def test_timeout_consumed(self):
  def fail(*a): raise TimeoutError()
  with self.assertRaises(TimeoutError): execute(E,self.marker,fail)
  with self.assertRaises(FileExistsError): execute(E,self.marker,self.send)
 def test_wrong_scope(self):
  def bad(*a): return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"version":1,"goals":["overview"]}'}]}]}
  with self.assertRaises(PermissionError): execute(E,self.marker,bad)
 def test_incomplete(self):
  with self.assertRaises(ValueError): execute(E,self.marker,lambda *a:{'status':'incomplete'})
