"""Offline, safe and complete receipt diagnostics for trial two."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import trial2_proposal_trial as trial2
from one_shot_proposal_trial import OnceHTTPClient,BRANCH,REPO
from response_envelope_diagnostics import extract_response_metadata
from safe_trial_diagnostics import safe_failure_record

class BoundedResponseReceiptTests(unittest.TestCase):
    def env(self):
        return {
            "AGI_TRIAL2_EXPLICIT_APPROVAL":"YES-TRIAL-2",
            "GITHUB_EVENT_NAME":"workflow_dispatch",
            "GITHUB_REF":BRANCH,
            "GITHUB_REPOSITORY":REPO,
            "GITHUB_RUN_ATTEMPT":"1",
            "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
            "OPENAI_PROJECT_ID":"proj_TEST1234567890",
            "OPENAI_API_KEY":"sk-"+"x"*48
        }
    def run_with_response(self,response):
        class Response:
            status=200
            def __init__(self,payload):self.payload=payload
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return json.dumps(self.payload).encode()
        class Opener:
            def __init__(self):self.calls=0
            def open(self,request,timeout):
                self.calls+=1
                return Response(response)
        opener=Opener()
        client=OnceHTTPClient("sk-"+"x"*48,"proj_TEST1234567890",opener=opener,
                              output_token_cap=1600)
        with (patch("sys.argv",["trial2","--live"]),
              patch.object(trial2.os,"environ",self.env()),
              patch.object(trial2,"OnceHTTPClient",return_value=client)):
            output=io.StringIO()
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as err:trial2.main()
        return json.loads(output.getvalue()),opener.calls,err.exception.code
    def test_incomplete_has_safe_counts(self):
        fake_secret="sk-DO-NOT-REVEAL-123"
        receipt,calls,exit_code=self.run_with_response({
            "status":"incomplete",
            "incomplete_details":{"reason":"max_output_tokens"},
            "output":[{"type":"reasoning","summary":[{"text":fake_secret}]}],
            "usage":{"input_tokens":85,"output_tokens":1600,
                     "output_tokens_details":{"reasoning_tokens":1500}},
            "id":fake_secret})
        self.assertEqual(calls,1)
        self.assertEqual(exit_code,1)
        self.assertEqual(receipt["failure_category"],"OUTPUT_TOKEN_BUDGET_EXHAUSTED")
        self.assertTrue(receipt["request_may_have_been_billed"])
        self.assertEqual(receipt["response_metadata"]["reasoning_tokens"],1500)
        self.assertEqual(receipt["response_metadata"]["output_tokens"],1600)
        self.assertNotIn(fake_secret,json.dumps(receipt))
    def test_unrecognized_response_metadata_has_no_private_text(self):
        secret="https://secret.invalid"
        receipt,calls,code=self.run_with_response({
            "status":"failed",
            "incomplete_details":{"reason":secret},
            "output":[{"type":"message","content":[{"type":"refusal","refusal":secret}]}],
            "usage":{"input_tokens":True,"output_tokens":-5}})
        self.assertEqual(calls,1)
        self.assertEqual(code,1)
        self.assertEqual(receipt["response_metadata"]["response_status"],"failed")
        self.assertEqual(receipt["response_metadata"]["incomplete_reason"],"none_or_other")
        self.assertIsNone(receipt["response_metadata"]["input_tokens"])
        self.assertNotIn(secret,json.dumps(receipt))
    def test_external_dict_never_accepted_as_safe_metadata(self):
        fake={"response_status":"sk-SECRET"}
        record=safe_failure_record(ValueError("invalid"),attempted_request=True,
                                   metadata=fake)
        self.assertNotIn("response_metadata",record)
    def test_no_response_no_metadata(self):
        rec=safe_failure_record(PermissionError("no key"),attempted_request=False)
        self.assertNotIn("response_metadata",rec)
        self.assertFalse(rec["request_may_have_been_billed"])
if __name__=="__main__":unittest.main()
