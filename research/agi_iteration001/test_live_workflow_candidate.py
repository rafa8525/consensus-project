"""Security review of the *inert* draft workflow in research/, no YAML execution."""
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
DRAFT=ROOT/"LIVE_WORKFLOW_CANDIDATE.yml"

class SecurityDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=DRAFT.read_text(encoding="utf8")
    def test_not_installed_in_actions(self):
        self.assertTrue(DRAFT.is_file())
        self.assertNotIn("/.github/workflows/",str(DRAFT))
    def test_manual_only(self):
        s=self.text
        self.assertIn("workflow_dispatch:",s)
        for marker in ("\n  push:","\n  pull_request:","\n  schedule:","\n  repository_dispatch:"):
            self.assertNotIn(marker,s)
    def test_approval_and_branch(self):
        s=self.text
        for x in ("agi-research-live","YES-REVIEWED",
                  "refs/heads/research/agi-iteration-001-20261119",
                  "rafa8525/consensus-project",
                  "github.run_attempt == 1"):
            self.assertIn(x,s)
    def test_pinned_code(self):
        self.assertIn("10d829304ec11f4d036d8c882c2f24047f1922ad",self.text)
        self.assertIn('rev-parse HEAD',self.text)
        self.assertIn('checkout --detach "$PINNED_RESEARCH_SHA"',self.text)
    def test_only_environment_secret(self):
        self.assertIn("secrets.OPENAI_API_KEY",self.text)
        self.assertIn("vars.OPENAI_PROJECT_ID",self.text)
        self.assertNotIn("secrets.GITHUB_TOKEN",self.text)
    def test_not_using_mutable_third_party_actions(self):
        self.assertNotIn("- uses:",self.text)
        self.assertIn("contents: read",self.text)
    def test_one_step_only_live_command(self):
        self.assertEqual(self.text.count("python3 one_shot_proposal_trial.py --live"),1)
    def test_no_direct_API_request_in_yaml(self):
        self.assertNotIn("curl -",self.text)
        self.assertNotIn("wget ",self.text)
if __name__=="__main__":unittest.main()
