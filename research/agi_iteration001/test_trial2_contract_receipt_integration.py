"""Simulated trial2 HTTP transport receipt after a schema-valid but disallowed proposal.

Never uses OpenAI or GitHub secrets, never sends a network request.
"""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import trial2_proposal_trial as trial
from one_shot_proposal_trial import OnceHTTPClient, BRANCH, REPO
from proposal_provider import OfflineProposalProvider

class ContractReceiptIntegrationTests(unittest.TestCase):
    def env(self):
        return {"AGI_TRIAL2_EXPLICIT_APPROVAL":"YES-TRIAL-2",
                "GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REF":BRANCH,"GITHUB_REPOSITORY":REPO,
                "GITHUB_RUN_ATTEMPT":"1",
                "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
                "OPENAI_PROJECT_ID":"proj_TEST1234567890",
                "OPENAI_API_KEY":"sk-"+"X"*48}
    def run_one(self,proposal):
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):
                raw={"status":"completed","id":"sk-private-NOT-FOR-LOGS",
                     "usage":{"input_tokens":275,"output_tokens":191,
                              "output_tokens_details":{"reasoning_tokens":0}},
                     "output":[{"type":"message","content":[
                          {"type":"output_text","text":json.dumps(proposal)}]}]}
                return json.dumps(raw).encode("utf-8")
        class Opener:
            calls=0
            def open(self,request,timeout):
                self.calls+=1
                return Response()
        opener=Opener()
        client=OnceHTTPClient("sk-"+"X"*48,"proj_TEST1234567890",
                              opener=opener,output_token_cap=1600)
        with (patch("sys.argv",["trial2","--live"]),
              patch.object(trial.os,"environ",self.env()),
              patch.object(trial,"OnceHTTPClient",return_value=client)):
            capture=io.StringIO()
            with redirect_stdout(capture):
                with self.assertRaises(SystemExit) as e:trial.main()
        return json.loads(capture.getvalue()),opener.calls,e.exception.code
    def test_completed_but_unapproved_dataset(self):
        p=json.loads(OfflineProposalProvider().propose())
        p["dataset_ids"]=["validation-v1","train-v1"]
        for alt in p["alternatives"]:
            alt.setdefault("n",None)
            alt.setdefault("alpha",None)
        result,calls,status=self.run_one(p)
        self.assertEqual(status,1)
        self.assertEqual(calls,1)
        self.assertEqual(result["failure_category"],"PROPOSAL_VALIDATION_FAILED")
        self.assertEqual(result["validation_reason"],"DATASET_MISMATCH")
        self.assertEqual(result["response_metadata"]["response_status"],"completed")
        self.assertEqual(result["response_metadata"]["input_tokens"],275)
        self.assertEqual(result["response_metadata"]["output_tokens"],191)
        self.assertTrue(result["request_may_have_been_billed"])
        self.assertFalse(result["automatic_retry_permitted"])
        self.assertNotIn("sk-private",json.dumps(result))
        self.assertNotIn("validation-v1",json.dumps(result))
    def test_completed_but_invalid_hypothesis(self):
        p=json.loads(OfflineProposalProvider().propose())
        p["hypothesis"]="sk-private-NEVER"
        for alt in p["alternatives"]:
            alt.setdefault("n",None)
            alt.setdefault("alpha",None)
        result,calls,status=self.run_one(p)
        self.assertEqual((calls,status),(1,1))
        self.assertEqual(result["validation_reason"],"HYPOTHESIS_TEXT")
        self.assertNotIn("sk-private",json.dumps(result))
if __name__=="__main__":unittest.main()
