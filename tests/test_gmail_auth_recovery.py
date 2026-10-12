"""Gmail OAuth recovery must preserve old tokens unless API verification succeeds."""
import os
import stat
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import gmail_auth_setup as oauth


class GmailRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.token = self.base / "token_gmail.json"
        self.client = self.base / "credentials.json"
        self.client.write_text("{}")
        self.token.write_text("existing-valid-token")
        self.addCleanup(patch.stopall)

    def test_atomic_private_token_replacement(self):
        creds = types.SimpleNamespace(to_json=lambda: '{"token":"fresh"}')
        oauth.persist_token_safely(self.token, creds)
        self.assertEqual(self.token.read_text(), '{"token":"fresh"}')
        self.assertEqual(stat.S_IMODE(self.token.stat().st_mode), 0o600)

    def test_failed_replace_keeps_previous_token(self):
        creds = types.SimpleNamespace(to_json=lambda: '{"token":"fresh"}')
        with patch.object(oauth.os, "replace", side_effect=OSError("failure")):
            with self.assertRaises(OSError):
                oauth.persist_token_safely(self.token, creds)
        self.assertEqual(self.token.read_text(), "existing-valid-token")

    def test_verification_failure_does_not_overwrite_token(self):
        credentials = types.SimpleNamespace(refresh_token="test")
        flow = types.SimpleNamespace(
            authorization_url=lambda **kw: ("https://example.invalid/authorize", "state"),
            fetch_token=lambda **kw: None,
            credentials=credentials,
        )
        with patch.object(oauth, "CREDENTIALS_FILE", self.client), \
             patch.object(oauth, "TOKEN_FILE", self.token), \
             patch("builtins.input", return_value="http://localhost/?code=test"), \
             patch.object(oauth, "verify_gmail_credentials", return_value=False), \
             patch.dict("sys.modules", {"google_auth_oauthlib": types.ModuleType("google_auth_oauthlib"),
                                        "google_auth_oauthlib.flow": types.SimpleNamespace(
                                            InstalledAppFlow=types.SimpleNamespace(
                                                from_client_secrets_file=lambda *a: flow))}):
            self.assertFalse(oauth.authenticate_gmail())
        self.assertEqual(self.token.read_text(), "existing-valid-token")

    def test_missing_refresh_token_keeps_existing_token(self):
        credentials = types.SimpleNamespace(refresh_token=None)
        flow = types.SimpleNamespace(
            authorization_url=lambda **kw: ("https://example.invalid/authorize", "state"),
            fetch_token=lambda **kw: None,
            credentials=credentials,
        )
        with patch.object(oauth, "CREDENTIALS_FILE", self.client), \
             patch.object(oauth, "TOKEN_FILE", self.token), \
             patch("builtins.input", return_value="http://localhost/?code=test"), \
             patch.dict("sys.modules", {"google_auth_oauthlib": types.ModuleType("google_auth_oauthlib"),
                                        "google_auth_oauthlib.flow": types.SimpleNamespace(
                                            InstalledAppFlow=types.SimpleNamespace(
                                                from_client_secrets_file=lambda *a: flow))}):
            self.assertFalse(oauth.authenticate_gmail())
        self.assertEqual(self.token.read_text(), "existing-valid-token")


if __name__ == "__main__":
    unittest.main()
