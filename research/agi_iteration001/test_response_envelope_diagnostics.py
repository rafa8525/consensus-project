import json
import unittest
from response_envelope_diagnostics import (
    extract_response_metadata,safe_diagnostic_code)

class ResponseEnvelopeDiagnosticsTests(unittest.TestCase):
    def test_reasoning_budget_exhausted(self):
        raw={"status":"incomplete","incomplete_details":{"reason":"max_output_tokens"},
          "output":[{"type":"reasoning","summary":[]}],
          "usage":{"input_tokens":120,"output_tokens":523,
                   "output_tokens_details":{"reasoning_tokens":523}}}
        m=extract_response_metadata(raw)
        self.assertEqual(m.incomplete_reason,"max_output_tokens")
        self.assertEqual(m.reasoning_tokens,523)
        self.assertFalse(m.output_text_present)
        self.assertEqual(safe_diagnostic_code(m),"OUTPUT_TOKEN_BUDGET_EXHAUSTED")
    def test_completed_with_json(self):
        raw={"status":"completed","output":[{"type":"reasoning"},
             {"type":"message","content":[{"type":"output_text","text":"{}"}]}],
             "usage":{"input_tokens":20,"output_tokens":50,
                      "output_tokens_details":{"reasoning_tokens":10}}}
        m=extract_response_metadata(raw)
        self.assertEqual(safe_diagnostic_code(m),"RESPONSE_ENVELOPE_OK")
        self.assertEqual(m.reasoning_tokens,10)
    def test_refusal(self):
        raw={"status":"completed","output":[{"type":"message",
              "content":[{"type":"refusal","refusal":"private content"}]}]}
        m=extract_response_metadata(raw)
        self.assertTrue(m.refusal_present)
        self.assertEqual(safe_diagnostic_code(m),"RESPONSE_INCOMPLETE_OR_REFUSED")
    def test_no_text(self):
        m=extract_response_metadata({"status":"completed","output":[]})
        self.assertEqual(safe_diagnostic_code(m),"RESPONSE_TEXT_MISSING")
    def test_no_raw_message_leaks(self):
        sentinel="sk-very-secret-NEVER-EMIT"
        m=extract_response_metadata({"status":"failed",
           "incomplete_details":{"reason":sentinel},
           "output":[{"type":"message","content":[{"type":"refusal","refusal":sentinel}]}],
           "usage":{"input_tokens":1,"output_tokens":2}})
        self.assertNotIn(sentinel,json.dumps(m.as_dict()))
    def test_unknown_enums_fail_closed(self):
        m=extract_response_metadata({"status":"unknown-secret","output":[]})
        self.assertEqual(m.status,"unknown")
        self.assertEqual(safe_diagnostic_code(m),"RESPONSE_INCOMPLETE_OR_REFUSED")
    def test_unknown_usage_values_ignored(self):
        m=extract_response_metadata({"status":"incomplete","usage":{
           "input_tokens":True,"output_tokens":-1,
           "output_tokens_details":{"reasoning_tokens":"SECRET"}}})
        self.assertIsNone(m.input_tokens)
        self.assertIsNone(m.output_tokens)
        self.assertIsNone(m.reasoning_tokens)
    def test_invalid_envelope(self):
        with self.assertRaises(ValueError):extract_response_metadata(None)
if __name__=="__main__":unittest.main()
