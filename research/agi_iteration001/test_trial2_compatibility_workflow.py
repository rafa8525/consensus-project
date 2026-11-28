"""Static verification of non-executable compatibility-review workflow."""
import unittest
from pathlib import Path

DRAFT=Path(__file__).parent/"TRIAL2_COMPATIBILITY_REVIEW_20261124.yml"
PIN="b2ad3746297e003b030889ccdb8970284f8e6a47"

class CompatibilityWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=DRAFT.read_text("utf-8")
    def test_uninstalled_review_only(self):
        self.assertTrue(DRAFT.exists())
        self.assertNotIn("/.github/workflows/",str(DRAFT))
        self.assertIn("has NOT been installed",self.text)
    def test_exact_pin(self):
        self.assertIn("PINNED_RESEARCH_SHA: "+PIN,self.text)
        self.assertIn('checkout --detach "$PINNED_RESEARCH_SHA"',self.text)
        self.assertIn("rev-parse HEAD",self.text)
    def test_manual_only(self):
        self.assertIn("workflow_dispatch:",self.text)
        for term in ("\n  push:","\n  schedule:","\n  pull_request:","\n  repository_dispatch:"):
            self.assertNotIn(term,self.text)
    def test_guarded_call(self):
        for term in ("agi-research-live","YES-TRIAL-2",
                     "github.run_attempt == 1",
                     "refs/heads/research/agi-iteration-001-20261119",
                     "secrets.OPENAI_API_KEY","vars.OPENAI_PROJECT_ID"):
            self.assertIn(term,self.text)
        self.assertEqual(self.text.count("python3 trial2_proposal_trial.py --live"),1)
        self.assertNotIn("- uses:",self.text)
if __name__=="__main__":unittest.main()
