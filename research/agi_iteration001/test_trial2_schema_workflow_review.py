"""Contract repair candidate is inert and preserves the experiment approval gates."""
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
DRAFT=ROOT/"TRIAL2_SCHEMA_REPAIR_WORKFLOW_REVIEW_20261124.yml"
PIN="3957ef772fabb8d1c72bccc1b070869eb4ac9174"

class Trial2SchemaWorkflowCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=DRAFT.read_text("utf-8")
    def test_inert_location_and_pinned_commit(self):
        self.assertNotIn("/.github/workflows/",str(DRAFT))
        self.assertIn("REVIEW-ONLY CANDIDATE",self.content)
        self.assertIn("PINNED_RESEARCH_SHA: "+PIN,self.content)
        self.assertIn('rev-parse HEAD',self.content)
    def test_only_manual_triggers(self):
        self.assertIn("workflow_dispatch:",self.content)
        for key in ("\n  push:","\n  schedule:","\n  pull_request:",
                    "\n  repository_dispatch:"):
            self.assertNotIn(key,self.content)
    def test_no_silent_spending_or_production_access(self):
        for key in ("github.run_attempt == 1","YES-TRIAL-2",
                    "environment: agi-research-live",
                    "refs/heads/research/agi-iteration-001-20261119",
                    "secrets.OPENAI_API_KEY","vars.OPENAI_PROJECT_ID",
                    "permissions:\n  contents: read"):
            self.assertIn(key,self.content)
        self.assertEqual(self.content.count("python3 trial2_proposal_trial.py --live"),1)
        self.assertNotIn("- uses:",self.content)
if __name__=="__main__": unittest.main()
