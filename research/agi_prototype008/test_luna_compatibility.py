import unittest, tempfile, pathlib
from unittest.mock import patch
from live_preflight import request_body, MODEL
from one_shot import execute, validate_gate, transport
from test_one_shot import E
class LunaCompatibility(unittest.TestCase):
 def test_model(self): self.assertEqual(MODEL,'gpt-6-luna'); self.assertEqual(request_body()['model'],MODEL)
 def test_legacy_denied(self):
  with self.assertRaises(PermissionError): validate_gate(dict(E,AGI_ALLOWED_MODEL='gpt-5-mini'))
 def test_standard_low(self):
  b=request_body();self.assertEqual(b['service_tier'],'default');self.assertEqual(b['reasoning'],{'effort':'low'})
 def test_schema(self):
  f=request_body()['text']['format'];self.assertEqual(f['type'],'json_schema');self.assertTrue(f['strict']);self.assertFalse(f['schema']['additionalProperties'])
 def test_transport_mock(self):
  with patch('one_shot.urllib.request.build_opener') as opener:
   opener.return_value.open.return_value.__enter__.return_value.read.return_value=b'{"status":"completed"}'
   self.assertEqual(transport(request_body(),E),{'status':'completed'})
   req=opener.return_value.open.call_args.args[0];self.assertEqual(req.full_url,'https://api.openai.com/v1/responses');self.assertEqual(req.get_method(),'POST');self.assertEqual(opener.return_value.open.call_count,1)
