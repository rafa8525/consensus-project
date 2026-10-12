"""ACS-05 token refresh persistence is atomic and permission restricted."""
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.continuity_guardian_agent import persist_refreshed_token


class GmailTokenPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "token_gmail.json"

    def test_new_file_is_private(self):
        persist_refreshed_token(self.path, '{"token":"new"}')
        self.assertEqual(self.path.read_text(), '{"token":"new"}')
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)

    def test_existing_token_replaced_atomically(self):
        self.path.write_text('{"token":"old"}')
        persist_refreshed_token(self.path, '{"token":"fresh"}')
        self.assertEqual(self.path.read_text(), '{"token":"fresh"}')
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertEqual(list(self.path.parent.glob(".gmail-token-*")), [])

    def test_failed_replace_preserves_previous_token(self):
        self.path.write_text('{"token":"old"}')
        with patch("agents.continuity_guardian_agent.os.replace",
                   side_effect=OSError("simulated disk failure")):
            with self.assertRaises(OSError):
                persist_refreshed_token(self.path, '{"token":"new"}')
        self.assertEqual(self.path.read_text(), '{"token":"old"}')
        self.assertEqual(list(self.path.parent.glob(".gmail-token-*")), [])


if __name__ == "__main__":
    unittest.main()
