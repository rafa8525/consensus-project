import unittest,tempfile
from skills_engine import Engine
T='2026-11-28T10:00:00+00:00'; L='2026-11-29T10:00:00+00:00'
class Test(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.e=Engine(self.tmp.name)
 def tearDown(self): self.e.close(); self.tmp.cleanup()
 def test_briefing(self):
  g=self.e.start('briefing','day1',T); r=self.e.run(g,dict(calendar=[],bills=[],packages=[]),T); self.assertEqual(r['state'],'reported_complete'); self.assertTrue(all(t['status']=='verified' for t in r['tasks']))
 def test_recurring(self): self.assertNotEqual(self.e.start('briefing','day1',T),self.e.start('briefing','day2',L))
 def test_idempotence(self): self.assertEqual(self.e.start('bill','1',T),self.e.start('bill','1',T))
 def test_conflict(self):
  self.e.start('bill','1',T)
  with self.assertRaises(ValueError): self.e.start('bill','1',L)
 def test_unsupported(self):
  with self.assertRaises(ValueError): self.e.start('send email','1',T)
 def test_false_confirmation(self):
  g=self.e.start('bill','1',T); r=self.e.run(g,{'bills':[],'payment_confirmation':True},L); self.assertEqual(r['state'],'overdue')
 def test_provider_cannot_confirm(self):
  g=self.e.start('bill','1',T)
  with self.assertRaises(PermissionError): self.e.evidence(g,'x','user_confirmed',T,'synthetic_provider')
 def test_reply_not_complete(self):
  g=self.e.start('bill','1',T); self.e.evidence(g,'x','reply_received',T,'synthetic_provider'); self.assertEqual(self.e.run(g,{'bills':[]},L)['state'],'reply_needs_review')
 def test_resume(self):
  g=self.e.start('appointment','1',T); self.e.run(g,{'calendar':[]},L); self.e.close(); self.e=Engine(self.tmp.name); self.e.evidence(g,'x','user_confirmed',L,'synthetic_user'); self.assertEqual(self.e.run(g,{'calendar':[]},L)['state'],'confirmed')
 def test_duplicate(self):
  g=self.e.start('bill','1',T); self.assertEqual(self.e.run(g,{'bills':[]},L)['notice'],'overdue'); self.assertIsNone(self.e.run(g,{'bills':[]},L)['notice'])
 def test_feedback(self):
  g=self.e.start('bill','1',T); self.e.feedback(g,'f',True); self.e.feedback(g,'f',True); self.assertEqual(self.e.skill_stats()['bill'],{'ratings':1,'positive':1})
 def test_retry(self):
  g=self.e.start('briefing','1',T); self.e.run(g,{},T); self.assertEqual(self.e.run(g,dict(calendar=[],bills=[],packages=[]),T)['state'],'reported_complete')
 def test_plan_tamper(self):
  g=self.e.start('bill','1',T); self.e.a.db.execute('UPDATE executions SET plan=? WHERE id=?',('pay bill',g)); self.e.a.db.commit()
  with self.assertRaises(ValueError): self.e.run(g,{},T)
if __name__=='__main__': unittest.main()
