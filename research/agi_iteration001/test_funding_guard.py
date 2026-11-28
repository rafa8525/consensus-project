import unittest
from funding_guard import FundingState,assessment

class FundingGuardTests(unittest.TestCase):
    def test_unfunded_blocks(self):
        r=assessment(FundingState())
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(r["reason"],"NO_PREPAID_CREDITS")
        self.assertFalse(r["api_call_permitted"])
    def test_no_purchase_even_if_funded(self):
        r=assessment(FundingState(organization_available_credit_usd="5.00"))
        self.assertFalse(r["credit_purchase_permitted"])
        self.assertFalse(r["api_call_permitted"])
    def test_user_declined_purchase(self):
        r=assessment(FundingState(user_approved_credit_purchase=False))
        self.assertEqual(r["purchase_attempts"],0)
    def test_auto_reload_never_allowed(self):
        r=assessment(FundingState(organization_available_credit_usd="5",auto_reload_enabled=True))
        self.assertEqual(r["reason"],"AUTO_RELOAD_MUST_BE_OFF")
    def test_cap_over_one_blocks(self):
        r=assessment(FundingState(organization_available_credit_usd="5",project_limit_usd="2"))
        self.assertEqual(r["reason"],"PROJECT_HARD_LIMIT_UNVERIFIED")
    def test_invalid_billing_data_blocks(self):
        for amount in ("NaN","-1","infinite",""):
            r=assessment(FundingState(organization_available_credit_usd=amount))
            self.assertEqual(r["status"],"BLOCKED")
    def test_cannot_grant_call_from_bool(self):
        state=FundingState(user_approved_credit_purchase=True,organization_available_credit_usd="5")
        self.assertFalse(assessment(state)["api_call_permitted"])
if __name__=="__main__":unittest.main()
