"""Trial #2 low-reasoning request contract; entirely fake clients and data."""
import json
import unittest
from types import SimpleNamespace
from openai_proposal_adapter import OpenAIProposalProvider
from one_shot_proposal_trial import OnceHTTPClient,live_once,BRANCH,REPO,MODEL
from proposal_provider import OfflineProposalProvider

class Trial2ReasoningBudgetTests(unittest.TestCase):
    def fake_env(self):
        return {"GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":BRANCH,
                "GITHUB_REPOSITORY":REPO,"GITHUB_RUN_ATTEMPT":"1",
                "AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED",
                "OPENAI_API_KEY":"sk-"+"x"*48,
                "OPENAI_PROJECT_ID":"proj_TEST1234567890"}
    def test_luna_reasoning_none_exact_one_call(self):
        class Fake:
            def __init__(self):self.responses=self;self.calls=[]
            def create(self,**kwargs):
                self.calls.append(kwargs)
                obj=json.loads(OfflineProposalProvider().propose())
                for alt in obj["alternatives"]:
                    alt.setdefault("n",None)
                    alt.setdefault("alpha",None)
                return SimpleNamespace(status="completed",output_text=json.dumps(obj))
        f=Fake()
        receipt=live_once(self.fake_env(),transport=f,output_token_cap=1600,reasoning_effort="none")
        self.assertEqual(receipt["status"],"ONE_PROPOSAL_RECEIVED")
        self.assertEqual(len(f.calls),1)
        self.assertEqual(f.calls[0]["reasoning"],{"effort":"none"})
        self.assertEqual(f.calls[0]["max_output_tokens"],1600)
        self.assertEqual(f.calls[0]["model"],MODEL)
        self.assertEqual(f.calls[0]["tools"],[])
        self.assertIs(f.calls[0]["store"],False)
    def test_old_trial_keeps_default_reasoning_unchanged(self):
        class Fake:
            def __init__(self):self.responses=self;self.kw=None
            def create(self,**kw):
                self.kw=kw
                from openai_proposal_adapter import normalize_for_executor
                obj=json.loads(OfflineProposalProvider().propose())
                for alt in obj["alternatives"]:
                    alt.setdefault("n",None)
                    alt.setdefault("alpha",None)
                return SimpleNamespace(status="completed",output_text=json.dumps(obj))
        fake=Fake()
        live_once(self.fake_env(),transport=fake)
        self.assertNotIn("reasoning",fake.kw)
    def test_other_effort_rejected(self):
        with self.assertRaises(ValueError):
            OpenAIProposalProvider(client=SimpleNamespace(responses=object()),
                model=MODEL,enabled=True,reasoning_effort="high")
    def test_transport_rejects_unapproved_reasoning(self):
        class Opener:
            def __init__(self):self.calls=0
            def open(self,*args,**kwargs):
                self.calls+=1
                raise OSError("Unexpected network")
        opener=Opener()
        client=OnceHTTPClient("sk-"+"x"*48,"proj_TEST1234567890",opener=opener,
                              output_token_cap=1600)
        payload=dict(model=MODEL,instructions="test",input="test",
                     max_output_tokens=1600,tools=[],store=False,
                     text={"format":{"type":"json_schema"}},
                     reasoning={"effort":"high"})
        with self.assertRaises(ValueError):client.create(**payload)
        self.assertEqual(opener.calls,0)
if __name__=="__main__":unittest.main()
