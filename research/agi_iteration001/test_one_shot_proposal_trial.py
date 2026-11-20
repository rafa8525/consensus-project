import unittest
from types import SimpleNamespace
from one_shot_proposal_trial import (
    MODEL,BRANCH,REPO,OnceHTTPClient,dry_run,verify_manual_context,live_once)

class OneShotTrialTests(unittest.TestCase):
    def test_dry_run_zero_calls(self):
        r=dry_run()
        self.assertEqual(r["external_calls"],0)
        self.assertFalse(r["promotion_approved"])
    def test_no_workflow_context_blocks(self):
        with self.assertRaises(PermissionError):verify_manual_context({})
    def test_only_research_branch(self):
        e=self.example_env()
        e["GITHUB_REF"]="refs/heads/main"
        with self.assertRaises(PermissionError):verify_manual_context(e)
    def test_no_retries(self):
        e=self.example_env()
        e["GITHUB_RUN_ATTEMPT"]="2"
        with self.assertRaises(PermissionError):verify_manual_context(e)
    def test_no_key(self):
        e=self.example_env()
        e.pop("OPENAI_API_KEY")
        with self.assertRaises(PermissionError):verify_manual_context(e)
    def test_no_unreviewed_trigger(self):
        e=self.example_env()
        e["GITHUB_EVENT_NAME"]="push"
        with self.assertRaises(PermissionError):verify_manual_context(e)
    def test_project_scoped(self):
        e=self.example_env()
        e["OPENAI_PROJECT_ID"]="proj_invalid!"
        with self.assertRaises(PermissionError):verify_manual_context(e)
    def test_without_transport_no_call_if_guard_fails(self):
        with self.assertRaises(PermissionError):live_once({})
    def test_mock_response_one_call(self):
        class Fake:
            def __init__(self):
                self.responses=self
                self.calls=0
            def create(self,**kwargs):
                from proposal_provider import OfflineProposalProvider
                import json
                v=json.loads(OfflineProposalProvider().propose())
                for x in v["alternatives"]:
                    x.setdefault("n",None)
                    x.setdefault("alpha",None)
                self.calls+=1
                return SimpleNamespace(status="completed",output_text=json.dumps(v))
        f=Fake()
        result=live_once(self.example_env(),transport=f)
        self.assertEqual(result["external_calls"],1)
        self.assertEqual(f.calls,1)
        self.assertFalse(result["production_changes"])
    def test_bad_response_never_retries(self):
        class Fake:
            def __init__(self):self.responses=self;self.calls=0
            def create(self,**kw):self.calls+=1;return SimpleNamespace(status="incomplete",output_text=None)
        f=Fake()
        with self.assertRaises(ValueError):live_once(self.example_env(),transport=f)
        self.assertEqual(f.calls,1)
    def example_env(self):
        return {"GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":BRANCH,
          "GITHUB_REPOSITORY":REPO,"GITHUB_RUN_ATTEMPT":"1",
          "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
          "OPENAI_PROJECT_ID":"proj_TEST1234567890",
          "OPENAI_API_KEY":"sk-"+"x"*48}
    def test_transport_blocks_duplicate_calls(self):
        class FakeOpener:
            def __init__(self):self.calls=0
            def open(self,*args,**kwargs):
                self.calls+=1
                raise OSError("simulated failed network")
        opener=FakeOpener()
        client=OnceHTTPClient("sk-"+"x"*48,"proj_TEST1234567890",opener=opener)
        body=dict(model=MODEL,max_output_tokens=800,tools=[],store=False,
                  instructions="bounded",input="test",text={"format":"json_schema"})
        with self.assertRaises(OSError):client.create(**body)
        with self.assertRaises(PermissionError):client.create(**body)
        self.assertEqual(opener.calls,1)
if __name__=="__main__":unittest.main()
