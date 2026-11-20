import sqlite3
import tempfile
import unittest
from pathlib import Path
from api_call_admission import Approval,preflight,run_mocked_proposal
from proposal_provider import OfflineProposalProvider

def approved(**changes):
    values=dict(experiment_id="offline-model-comparison-v2",
                model="example-model",approved_by="offline-unit-test",
                approved_spend_usd="0.01",input_usd_per_million="1.00",
                output_usd_per_million="2.00",
                approved_api_project="not-a-real-project")
    values.update(changes)
    return Approval(**values)

class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"admission.db"
    def test_dry_run_under_budget(self):
        p=preflight(approved(),model="example-model",input_token_ceiling=500,
                    output_token_ceiling=800)
        self.assertEqual(p["estimated_upper_usd"],"0.00210")
        self.assertFalse(p["is_actual_billing_cap"])
    def test_live_denied_even_with_ample_estimate(self):
        with self.assertRaises(PermissionError):
            preflight(approved(),model="example-model",input_token_ceiling=500,
                      output_token_ceiling=800,live=True)
    def test_live_requires_two_attestations(self):
        with self.assertRaises(PermissionError):
            preflight(approved(live_calls_approved=True),model="example-model",
                      input_token_ceiling=500,output_token_ceiling=800,live=True)
    def test_approved_model_only(self):
        with self.assertRaises(PermissionError):
            preflight(approved(),model="unauthorized",input_token_ceiling=500,
                      output_token_ceiling=800)
    def test_budget_exceed(self):
        with self.assertRaises(PermissionError):
            preflight(approved(approved_spend_usd="0.0001"),
                      model="example-model",input_token_ceiling=500,output_token_ceiling=800)
    def test_negative_price(self):
        with self.assertRaises(ValueError):
            preflight(approved(output_usd_per_million="-1"),model="example-model",
                      input_token_ceiling=500,output_token_ceiling=800)
    def test_nan_price(self):
        with self.assertRaises(ValueError):
            preflight(approved(input_usd_per_million="NaN"),model="example-model",
                      input_token_ceiling=500,output_token_ceiling=800)
    def test_token_limit(self):
        with self.assertRaises(ValueError):
            preflight(approved(),model="example-model",
                      input_token_ceiling=500,output_token_ceiling=1001)
    def test_replayed_request_refused(self):
        result=run_mocked_proposal(self.db,approved(),
                   OfflineProposalProvider().propose,model="example-model")
        self.assertEqual(result["external_calls"],0)
        with self.assertRaises(sqlite3.IntegrityError):
            run_mocked_proposal(self.db,approved(),
                   OfflineProposalProvider().propose,model="example-model")
    def test_mock_injection_failed_receipt(self):
        with self.assertRaises(ValueError):
            run_mocked_proposal(self.db,approved(),lambda: '{"shell":"bash"}',
                                model="example-model")
        c=sqlite3.connect(self.db)
        try:
            self.assertEqual(c.execute("SELECT status FROM requests").fetchone()[0],"failed")
        finally:c.close()
    def test_mock_valid_receipt(self):
        result=run_mocked_proposal(self.db,approved(),OfflineProposalProvider().propose,
                                   model="example-model")
        self.assertEqual(result["provider"],"SIMULATED_NO_API")
        self.assertFalse(result["promotion_approved"])
        c=sqlite3.connect(self.db)
        try:
            self.assertEqual(c.execute("SELECT status FROM requests").fetchone()[0],"completed")
        finally:c.close()
    def test_unauthorized_fails_before_db(self):
        with self.assertRaises(PermissionError):
            run_mocked_proposal(self.db,approved(approved_spend_usd="0"),
                        OfflineProposalProvider().propose,model="example-model")
        self.assertFalse(self.db.exists())
if __name__=="__main__":unittest.main()
