"""No-cost contract regression tests after paid trial #2 rejection.
These tests use synthetic proposals and fake API clients only.
"""
import copy
import json
import unittest
from types import SimpleNamespace

from proposal_provider import (
    OfflineProposalProvider, ProposalValidationError, validate_proposal,
    DATASET_IDS, BUDGET, MODEL_CATALOG
)
from openai_proposal_adapter import (
    PROPOSAL_SCHEMA, normalize_for_executor, OpenAIProposalProvider
)
from safe_trial_diagnostics import safe_failure_record

def compliant():
    p=json.loads(OfflineProposalProvider().propose())
    p["alternatives"]=[dict(x,n=None,alpha=None) if x["kind"]=="word_nb"
                       else dict(x) for x in p["alternatives"]]
    return p

class Trial2ContractRepairTests(unittest.TestCase):
    def test_schema_narrows_known_contract(self):
        props=PROPOSAL_SCHEMA["properties"]
        self.assertEqual(props["dataset_ids"]["items"]["enum"],list(DATASET_IDS))
        self.assertEqual(props["compute_budget"]["properties"]["max_model_fits"]["enum"],[3])
        self.assertEqual(props["compute_budget"]["properties"]["max_examples"]["enum"],[30])
        alt=props["alternatives"]["items"]["properties"]
        self.assertEqual(alt["kind"]["enum"],["word_nb","word_char_nb"])
        self.assertEqual(alt["n"]["enum"],[None,3,4])
        self.assertEqual(alt["alpha"]["enum"],[None,0.5,1.0])
        self.assertEqual(props["stop_conditions"]["items"]["enum"],
                         ["at_most_three_fits","no_production_promotion"])
        self.assertFalse(PROPOSAL_SCHEMA["additionalProperties"])
        self.assertEqual(len(PROPOSAL_SCHEMA["required"]),8)
    def test_good_model_output_is_accepted(self):
        obj=normalize_for_executor(compliant())
        self.assertEqual(obj["alternatives"],list(MODEL_CATALOG))
        self.assertEqual(obj["dataset_ids"],list(DATASET_IDS))
    def test_all_field_errors_are_allowlisted(self):
        cases=[
            ("EXPERIMENT_ID",lambda p:p.update(experiment_id="!")),
            ("HYPOTHESIS_TEXT",lambda p:p.update(hypothesis="sk-test-key; DROP TABLE users")),
            ("FALSIFIER_TEXT",lambda p:p.update(expected_falsifier="short")),
            ("METRIC_MISMATCH",lambda p:p.update(metric="untrusted")),
            ("DATASET_MISMATCH",lambda p:p.update(dataset_ids=["validation-v1","train-v1"])),
            ("BUDGET_MISMATCH",lambda p:p.update(compute_budget={"max_model_fits":4,"max_examples":30})),
            ("STOP_CONDITION_MISMATCH",lambda p:p.update(stop_conditions=["no_production_promotion","at_most_three_fits"])),
            ("CANDIDATE_MISMATCH",lambda p:p["alternatives"].reverse()),
            ("RESPONSE_SHAPE",lambda p:p.pop("metric")),
        ]
        for expected,mutate in cases:
            with self.subTest(expected=expected):
                p=compliant()
                mutate(p)
                with self.assertRaises(ProposalValidationError) as ctx:
                    normalize_for_executor(p)
                receipt=safe_failure_record(ctx.exception,attempted_request=True)
                self.assertEqual(receipt["validation_reason"],expected)
                self.assertEqual(receipt["failure_category"],"PROPOSAL_VALIDATION_FAILED")
                self.assertNotIn("sk-test-key",json.dumps(receipt))
                self.assertFalse(receipt["automatic_retry_permitted"])
    def test_unknown_error_reason_cannot_leak(self):
        secret="sk-secret-never-log"
        err=ProposalValidationError(secret)
        self.assertEqual(safe_failure_record(err)["validation_reason"],"RESPONSE_SHAPE")
        self.assertNotIn(secret,json.dumps(safe_failure_record(err)))
    def test_bad_variant_not_silently_corrected(self):
        p=compliant()
        p["alternatives"][1]["alpha"]=10
        with self.assertRaises(ProposalValidationError) as ctx:
            normalize_for_executor(p)
        self.assertEqual(ctx.exception.reason,"CANDIDATE_MISMATCH")
    def test_fake_completed_api_response_one_call(self):
        class Fake:
            def __init__(self):
                self.responses=self
                self.calls=[]
            def create(self,**args):
                self.calls.append(args)
                return SimpleNamespace(status="completed",
                                       output_text=json.dumps(compliant()))
        client=Fake()
        provider=OpenAIProposalProvider(client=client,model="gpt-6-luna",
                                        enabled=True,max_output_tokens=1600,
                                        reasoning_effort="none")
        proposal=json.loads(provider.propose())
        validate_proposal(proposal)
        self.assertEqual(len(client.calls),1)
        self.assertEqual(client.calls[0]["reasoning"],{"effort":"none"})
        self.assertEqual(client.calls[0]["tools"],[])
        self.assertIs(client.calls[0]["store"],False)
        with self.assertRaises(RuntimeError):provider.propose()
if __name__=="__main__":unittest.main()
