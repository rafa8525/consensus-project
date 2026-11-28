import unittest
from live_trial_readiness import ReadinessEvidence, readiness

def claimed(**overrides):
    base=dict(project_verified=True,api_credential_scoped_to_project_verified=True,
        hard_limit_enabled_verified=True,project_limit_usd="1.00",
        existing_monthly_usage_usd="0",model_access_verified=True,
        input_rate_per_million_usd="1.00",output_rate_per_million_usd="2.00",
        model="test-model-id",verified_by="offline-test-only")
    base.update(overrides)
    return ReadinessEvidence(**base)

class ReadinessTests(unittest.TestCase):
    def test_blank_denied(self):
        r=readiness(ReadinessEvidence())
        self.assertEqual(r["status"],"BLOCKED")
        self.assertFalse(r["proposal_api_call_permitted"])
    def test_claims_not_actual_permission(self):
        r=readiness(claimed())
        self.assertEqual(r["status"],"READY_FOR_MANUAL_VERIFICATION")
        self.assertTrue(r["unverified_attestations"])
        self.assertFalse(r["proposal_api_call_permitted"])
    def test_soft_budget_not_enough(self):
        r=readiness(claimed(hard_limit_enabled_verified=False))
        self.assertEqual(r["status"],"BLOCKED")
    def test_over_one_usd_fails(self):
        self.assertEqual(readiness(claimed(project_limit_usd="10"))["status"],"BLOCKED")
    def test_insufficient_remaining_cap_fails(self):
        self.assertEqual(readiness(claimed(existing_monthly_usage_usd="0.40"))["status"],"BLOCKED")
    def test_missing_credential_fails(self):
        self.assertEqual(readiness(claimed(api_credential_scoped_to_project_verified=False))["status"],"BLOCKED")
    def test_bad_price_fails(self):
        self.assertEqual(readiness(claimed(output_rate_per_million_usd="NaN"))["status"],"BLOCKED")
    def test_unselected_model_fails(self):
        self.assertEqual(readiness(claimed(model=""))["status"],"BLOCKED")
    def test_never_authorizes_in_tests(self):
        for e in (ReadinessEvidence(),claimed(),claimed(project_verified=False)):
            r=readiness(e)
            self.assertFalse(r["proposal_api_call_permitted"])
            self.assertEqual(r["actual_spend_usd"],"0.00")

if __name__=="__main__":unittest.main()
