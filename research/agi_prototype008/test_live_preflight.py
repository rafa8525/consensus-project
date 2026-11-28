import unittest,json
from live_preflight import request_body,preflight,validate_response
class PreflightTests(unittest.TestCase):
 def test_disabled(self): self.assertFalse(preflight()['dispatch_enabled']);self.assertEqual(preflight()['requests_sent'],0)
 def test_cap(self): self.assertEqual(request_body()['max_output_tokens'],512)
 def test_privacy(self): self.assertFalse(request_body()['store']);self.assertNotIn('tools',request_body())
 def test_valid(self): self.assertEqual(validate_response(json.dumps({'version':1,'goals':['bill_tracking','appointment_tracking']})),('appointment','bill'))
 def test_scope(self):
  with self.assertRaises(PermissionError): validate_response('{"version":1,"goals":["overview"]}')
 def test_bad(self):
  with self.assertRaises(ValueError): validate_response('invalid')
