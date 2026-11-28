"""Static review tests for the non-executable repaired workflow candidate."""
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
DRAFT=ROOT/"TRIAL2_REPAIRED_WORKFLOW_REVIEW_20261124.yml"
PIN="a4b2bb28cae310a270afcb0716fb09a0fff77ade"

class RepairedTrial2WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yaml=DRAFT.read_text(encoding="utf-8")
    def test_inert_and_pinned(self):
        self.assertTrue(DRAFT.is_file())
        self.assertNotIn("/.github/workflows/",str(DRAFT))
        self.assertIn("PINNED_RESEARCH_SHA: "+PIN,self.yaml)
        self.assertIn('rev-parse HEAD',self.yaml)
    def test_manual_only(self):
        self.assertIn("workflow_dispatch:",self.yaml)
        for t in ("\n  push:","\n  schedule:","\n  pull_request:","\n  repository_dispatch:"):
            self.assertNotIn(t,self.yaml)
    def test_security_boundaries(self):
        for marker in ("agi-research-live","github.run_attempt == 1",
                        "YES-TRIAL-2","secrets.OPENAI_API_KEY",
                        "vars.OPENAI_PROJECT_ID","contents: read",
                        "refs/heads/research/agi-iteration-001-20261119"):
            self.assertIn(marker,self.yaml)
        self.assertEqual(self.yaml.count("python3 trial2_proposal_trial.py --live"),1)
        self.assertNotIn("- uses:",self.yaml)
    def test_uninstalled_warning(self):
        self.assertIn("has NOT been installed",self.yaml)
if __name__=="__main__": unittest.main()
