"""Offline evidence protocol tests: no secrets and no false research success."""
import json
import unittest
from proposal_evidence import proposal_evidence
from proposal_provider import OfflineProposalProvider

class ProposalEvidenceTests(unittest.TestCase):
    def test_fixed_catalog_and_digest_are_deterministic(self):
        p=OfflineProposalProvider().propose()
        a=proposal_evidence(p)
        b=proposal_evidence(p)
        self.assertEqual(a,b)
        self.assertEqual(len(a["proposal_sha256"]),64)
        self.assertEqual(len(a["candidate_models"]),3)
        self.assertFalse(a["experiment_executed"])
        self.assertFalse(a["measured_improvement"])
    def test_no_model_prose_is_reported(self):
        obj=json.loads(OfflineProposalProvider().propose())
        evidence=json.dumps(proposal_evidence(obj,origin="live_api"))
        self.assertNotIn(obj["hypothesis"],evidence)
        self.assertNotIn(obj["expected_falsifier"],evidence)
        self.assertNotIn(obj["experiment_id"],evidence)
        self.assertIn('"origin": "live_api"',evidence)
    def test_untrusted_variant_rejected(self):
        obj=json.loads(OfflineProposalProvider().propose())
        obj["alternatives"][1]["alpha"]=200
        with self.assertRaises(ValueError):proposal_evidence(obj)
    def test_invalid_origin_rejected(self):
        with self.assertRaises(ValueError):
            proposal_evidence(OfflineProposalProvider().propose(),origin="secret_external")
    def test_no_model_promotion_claim(self):
        result=proposal_evidence(OfflineProposalProvider().propose())
        self.assertFalse(result["promotion_approved"])
        self.assertTrue(result["review_required_for_full_model_text"])
        self.assertEqual(result["compute_budget"]["max_model_fits"],3)
if __name__=="__main__":unittest.main()
