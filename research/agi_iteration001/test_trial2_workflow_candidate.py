"""Static security checks of the inert second trial workflow draft."""
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
PIN="25f362ed74f3227e44df815eb376b70791cb4a85"

class Trial2CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=(ROOT/"TRIAL2_WORKFLOW_CANDIDATE.yml").read_text()
    def test_inert_location(self):
        self.assertTrue((ROOT/"TRIAL2_WORKFLOW_CANDIDATE.yml").is_file())
        self.assertNotIn("/.github/workflows/",str(ROOT/"TRIAL2_WORKFLOW_CANDIDATE.yml"))
    def test_manual_dispatch_only(self):
        s=self.text
        self.assertIn("workflow_dispatch:",s)
        for trigger in ("\n  push:","\n  pull_request:","\n  schedule:","\n  repository_dispatch:"):
            self.assertNotIn(trigger,s)
    def test_project_branch_and_confirmation(self):
        for marker in ("YES-TRIAL-2","agi-research-live",
            "refs/heads/research/agi-iteration-001-20261119",
            "rafa8525/consensus-project","github.run_attempt == 1"):
            self.assertIn(marker,self.text)
    def test_pin_and_single_command(self):
        self.assertIn(PIN,self.text)
        self.assertIn('checkout --detach "$PINNED_RESEARCH_SHA"',self.text)
        self.assertEqual(self.text.count("python3 trial2_proposal_trial.py --live"),1)
    def test_minimal_permissions_and_encrypted_key(self):
        self.assertIn("contents: read",self.text)
        self.assertIn("secrets.OPENAI_API_KEY",self.text)
        self.assertIn("vars.OPENAI_PROJECT_ID",self.text)
        self.assertNotIn("- uses:",self.text)
        self.assertNotIn("secrets.GITHUB_TOKEN",self.text)
if __name__=="__main__":unittest.main()
