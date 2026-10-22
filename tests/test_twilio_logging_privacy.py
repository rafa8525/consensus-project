"""Privacy regression tests: mocked Twilio, no network or real SMS."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import twilio_guard as guard

PHONE = "+15550009999"
BODY = "PRIVATE_TEST_MESSAGE_DO_NOT_LOG"
ERROR_TEXT = "PRIVATE_EXCEPTION_DO_NOT_LOG"

class FakeMessages:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError(ERROR_TEXT + " " + PHONE)
        return type("FakeMessage", (), {"sid": "SM_FAKE_LOCAL_TEST"})()

class FakeClient:
    def __init__(self, fail=False):
        self.messages = FakeMessages(fail)

class TwilioPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        base = Path(self.directory.name)
        self.sent = base / "sent.log"
        self.blocked = base / "blocked.log"
        for attr, path in (("SEND_LOG", self.sent),
                           ("LOG_FILE", self.blocked)):
            p = patch.object(guard, attr, path)
            p.start()
            self.addCleanup(p.stop)

    def log_text(self):
        return "".join(
            p.read_text(encoding="utf-8")
            for p in (self.sent, self.blocked) if p.exists()
        )

    def assert_private(self):
        text = self.log_text()
        for secret in (PHONE, BODY, ERROR_TEXT):
            self.assertNotIn(secret, text)

    def test_silence_prevents_sending_and_leakage(self):
        client = FakeClient()
        with patch.object(guard, "SILENCE", True), \
             patch.object(guard, "ENABLE_SEND", False):
            result = guard.send_sms(client, to=PHONE, body=BODY)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(client.messages.calls, 0)
        self.assert_private()

    def test_disabled_send_prevents_sending_and_leakage(self):
        client = FakeClient()
        with patch.object(guard, "SILENCE", False), \
             patch.object(guard, "ENABLE_SEND", False):
            result = guard.send_sms(client, to=PHONE, body=BODY)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(client.messages.calls, 0)
        self.assert_private()

    def test_mock_submission_excludes_personal_content(self):
        client = FakeClient()
        with patch.object(guard, "SILENCE", False), \
             patch.object(guard, "ENABLE_SEND", True), \
             patch.object(guard, "_rate_ok", return_value=True):
            result = guard.send_sms(client, to=PHONE, body=BODY)
        self.assertEqual(result["status"], "sent")
        self.assertEqual(client.messages.calls, 1)
        self.assertIn("SM_FAKE_LOCAL_TEST", self.log_text())
        self.assert_private()

    def test_mock_exception_excludes_error_details(self):
        client = FakeClient(fail=True)
        with patch.object(guard, "SILENCE", False), \
             patch.object(guard, "ENABLE_SEND", True), \
             patch.object(guard, "_rate_ok", return_value=True):
            with self.assertRaises(RuntimeError):
                guard.send_sms(client, to=PHONE, body=BODY)
        self.assert_private()

    def test_rate_limit_excludes_personal_content(self):
        client = FakeClient()
        with patch.object(guard, "SILENCE", False), \
             patch.object(guard, "ENABLE_SEND", True), \
             patch.object(guard, "_rate_ok", return_value=False):
            result = guard.send_sms(client, to=PHONE, body=BODY)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(client.messages.calls, 0)
        self.assert_private()

if __name__ == "__main__":
    unittest.main()
