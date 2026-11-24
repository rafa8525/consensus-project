import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
import trial2_proposal_trial as t
import one_shot_proposal_trial as old
from safe_trial_diagnostics import classify_failure

class SecondTrialTests(unittest.TestCase):
    def test_dry_run_has_no_network(self):
        with patch("sys.argv",["trial2","--dry-run"]),redirect_stdout(io.StringIO()) as stream:
            t.main()
        self.assertIn("TRIAL2_PREPARATION_ONLY",stream.getvalue())
    def test_missing_approval_blocks(self):
        with patch("sys.argv",["trial2","--live"]),patch.object(t.os,"environ",{}):
            with self.assertRaises(SystemExit) as ctx:t.main()
        self.assertIn("BLOCKED",str(ctx.exception))
    def test_second_budget_injected_once(self):
        env={"GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":old.BRANCH,
             "GITHUB_REPOSITORY":old.REPO,"GITHUB_RUN_ATTEMPT":"1",
             "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
             "OPENAI_PROJECT_ID":"proj_TEST1234567890",
             "OPENAI_API_KEY":"sk-"+"x"*48}
        class Fake:
            def __init__(self):self.responses=self;self.calls=0
            def create(self,**kw):
                self.calls+=1
                self.max_output=kw["max_output_tokens"]
                from proposal_provider import OfflineProposalProvider
                import json
                o=json.loads(OfflineProposalProvider().propose())
                for alt in o["alternatives"]:
                    alt.setdefault("n",None)
                    alt.setdefault("alpha",None)
                return SimpleNamespace(status="completed",output_text=json.dumps(o))
        fake=Fake()
        receipt=old.live_once(env,transport=fake,output_token_cap=1600)
        self.assertEqual(receipt["external_calls"],1)
        self.assertEqual(fake.calls,1)
        self.assertEqual(fake.max_output,1600)
    def test_token_cap_never_unbounded(self):
        with self.assertRaises(ValueError):
            old.OnceHTTPClient("sk-"+"x"*48,"proj_TEST1234567890",output_token_cap=50000)
    def test_no_duplicate_on_network_failure(self):
        class FakeOpener:
            def __init__(self):self.calls=0
            def open(self,request,timeout):
                self.calls+=1
                raise TimeoutError("private key or response not for logs")
        op=FakeOpener()
        cl=old.OnceHTTPClient("sk-"+"x"*48,"proj_TEST1234567890",
                              opener=op,output_token_cap=1600)
        payload={"model":old.MODEL,"instructions":"short","input":"short",
                 "max_output_tokens":1600,"tools":[],"store":False,
                 "text":{"format":{"type":"json_schema"}}}
        with self.assertRaises(TimeoutError):cl.create(**payload)
        with self.assertRaises(PermissionError):cl.create(**payload)
        self.assertEqual(op.calls,1)
    def test_preflight_failure_does_not_claim_possible_charge(self):
        with (patch("sys.argv",["trial2","--live"]),
              patch.object(t.os,"environ",
                           {"AGI_TRIAL2_EXPLICIT_APPROVAL":"YES-TRIAL-2"})):
            out=io.StringIO()
            with redirect_stdout(out):
                with self.assertRaises(SystemExit):t.main()
            import json
            receipt=json.loads(out.getvalue())
            self.assertEqual(receipt["failure_category"],"LOCAL_CONFIGURATION_BLOCKED")
            self.assertFalse(receipt["request_may_have_been_billed"])
    def test_cli_error_is_sanitized(self):
        env={"AGI_TRIAL2_EXPLICIT_APPROVAL":"YES-TRIAL-2",
             "GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":old.BRANCH,
             "GITHUB_REPOSITORY":old.REPO,"GITHUB_RUN_ATTEMPT":"1",
             "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
             "OPENAI_PROJECT_ID":"proj_TEST1234567890",
             "OPENAI_API_KEY":"sk-"+"x"*48}
        # A mocked transport records the call attempt and prevents any network use.
        client=SimpleNamespace(calls=1)
        with (patch("sys.argv",["trial2","--live"]),
              patch.object(t.os,"environ",env),
              patch.object(t,"OnceHTTPClient",return_value=client),
              patch.object(t,"live_once",side_effect=RuntimeError("sk-secret-NEVER"))):
            out=io.StringIO()
            with redirect_stdout(out):
                with self.assertRaises(SystemExit):t.main()
            import json
            receipt=json.loads(out.getvalue())
            self.assertNotIn("sk-secret",out.getvalue())
            self.assertEqual(receipt["failure_category"],"UNKNOWN_SAFE_FAILURE")
            self.assertTrue(receipt["request_may_have_been_billed"])
    def test_failure_without_attempt_reports_no_charge(self):
        env={"AGI_TRIAL2_EXPLICIT_APPROVAL":"YES-TRIAL-2",
             "GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":old.BRANCH,
             "GITHUB_REPOSITORY":old.REPO,"GITHUB_RUN_ATTEMPT":"1",
             "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
             "OPENAI_PROJECT_ID":"proj_TEST1234567890",
             "OPENAI_API_KEY":"sk-"+"x"*48}
        client=SimpleNamespace(calls=0)
        with (patch("sys.argv",["trial2","--live"]),
              patch.object(t.os,"environ",env),
              patch.object(t,"OnceHTTPClient",return_value=client),
              patch.object(t,"live_once",side_effect=ValueError("bad input"))):
            out=io.StringIO()
            with redirect_stdout(out):
                with self.assertRaises(SystemExit):t.main()
            import json
            self.assertFalse(json.loads(out.getvalue())["request_may_have_been_billed"])
if __name__=="__main__":unittest.main()
