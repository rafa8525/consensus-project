"""Regression guard: ACS-05 must never persist raw OAuth exception messages."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "agents/continuity_guardian_agent.py"

class OAuthRedactionTests(unittest.TestCase):
    def test_valid_python(self):
        ast.parse(SOURCE.read_text(encoding="utf-8"))

    def test_oauth_error_is_classified_without_raw_exception_in_critical(self):
        text = SOURCE.read_text(encoding="utf-8")
        begin = text.index("        # Inspect the error in memory, but never persist raw exception text:")
        end = text.index("\n\n    return creds_data, token_creds", begin)
        handler = text[begin:end]
        self.assertIn('"invalid_grant" in low', handler)
        self.assertIn('"invalid_client" in low', handler)
        self.assertNotIn("{exc}", handler)
        self.assertNotIn("{text}", handler)
        self.assertNotIn("CRITICAL.append(f", handler)

if __name__ == "__main__":
    unittest.main()
