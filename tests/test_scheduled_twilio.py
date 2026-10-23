"""Regression checks for scheduled ACS-05 Twilio configuration and safety."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common.twilio_config import load_existing_twilio_settings
from common import twilio_guard

class ScheduledTwilioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = {}
    def write(self, relative, body):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    def test_legacy_credentials_but_no_enable_remains_blocked(self):
        self.write("reminder-api/.env", "TWILIO_ACCOUNT_SID=ACexample\nTWILIO_AUTH_TOKEN=secret\nTWILIO_FROM_NUMBER=+1111\nTWILIO_TO_NUMBER=+1222\n")
        settings = load_existing_twilio_settings(self.root, self.env)
        self.assertEqual(settings["TWILIO_FROM_NUMBER"], "+1111")
        self.assertEqual(settings["TWILIO_ENABLE_SEND"], "0")
    def test_explicit_saved_opt_in_with_runtime_override(self):
        self.write("reminder-api/.env", "TWILIO_ENABLE_SEND=1\nTWILIO_SILENCE=0\n")
        settings = load_existing_twilio_settings(self.root, {"TWILIO_SILENCE": "1"})
        self.assertEqual(settings["TWILIO_ENABLE_SEND"], "1")
        self.assertEqual(settings["TWILIO_SILENCE"], "1")
    def test_guard_explicit_false_blocks_without_network(self):
        class Client:
            class messages:
                @staticmethod
                def create(**kwargs):
                    raise AssertionError("no network calls allowed")
        with patch.object(twilio_guard, "_log"):
            result = twilio_guard.send_sms(
                Client(), to="not-real", body="test",
                enable_send=False, silence=False)
        self.assertEqual(result["status"], "blocked")
    def test_guard_silence_blocks_even_when_opted_in(self):
        class Client:
            class messages:
                @staticmethod
                def create(**kwargs):
                    raise AssertionError("no network calls allowed")
        with patch.object(twilio_guard, "_log"):
            result = twilio_guard.send_sms(
                Client(), to="not-real", body="test",
                enable_send=True, silence=True)
        self.assertEqual(result["reason"], "silence")
    def test_guard_mock_delivery_requires_opt_in(self):
        class Client:
            class messages:
                @staticmethod
                def create(**kwargs):
                    return type("Msg", (), {"sid": "SMmock"})()
        with patch.object(twilio_guard, "_log"), patch.object(twilio_guard, "_rate_ok", return_value=True):
            result = twilio_guard.send_sms(
                Client(), to="not-real", body="test",
                enable_send=True, silence=False)
        self.assertEqual(result["status"], "sent")

if __name__ == "__main__":
    unittest.main()
