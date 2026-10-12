"""ACS-05 SMS delivery contract tests; no network, files or real SMS."""
import os
import sys
import types
import unittest
from unittest.mock import patch
from agents import continuity_guardian_agent as guardian


class SMSDeliveryTests(unittest.TestCase):
    def setUp(self):
        guardian.INFO.clear()
        guardian.WARN.clear()
        self.state = {}
        self.env = patch.dict(os.environ, {
            "TWILIO_ACCOUNT_SID": "fake",
            "TWILIO_AUTH_TOKEN": "fake",
            "TWILIO_FROM_NUMBER": "+10000000000",
            "TWILIO_TO_NUMBER": "+10000000001",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(guardian.INFO.clear)
        self.addCleanup(guardian.WARN.clear)

    def with_fake_guard(self, response, exception=None):
        rest = types.ModuleType("twilio.rest")
        rest.Client = lambda *a, **kw: object()
        twilio = types.ModuleType("twilio")
        twilio.rest = rest
        g = types.ModuleType("common.twilio_guard")
        calls = []
        def guarded_send(client, **kw):
            calls.append(kw)
            if exception is not None:
                raise exception
            return response
        g.send_sms = guarded_send
        with patch.dict(sys.modules, {"twilio": twilio, "twilio.rest": rest,
                                      "common.twilio_guard": g}):
            with patch("common.twilio_guard", g, create=True):
                guardian.maybe_send_sms("failure", "fingerprint", self.state)
        return calls

    def test_sent_records_fingerprint(self):
        calls = self.with_fake_guard({"status": "sent"})
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.state.get("last_alert_fingerprint"), "fingerprint")

    def test_blocked_does_not_claim_delivery(self):
        calls = self.with_fake_guard({"status": "blocked", "reason": "silence"})
        self.assertEqual(len(calls), 1)
        self.assertNotIn("last_alert_fingerprint", self.state)
        self.assertTrue(guardian.WARN)

    def test_failure_does_not_bypass_guard(self):
        calls = self.with_fake_guard(None, RuntimeError("simulated"))
        self.assertEqual(len(calls), 1)
        self.assertNotIn("last_alert_fingerprint", self.state)
        self.assertTrue(guardian.WARN)

    def test_missing_credentials_does_not_attempt_send(self):
        with patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": ""}):
            guardian.maybe_send_sms("failure", "fingerprint", self.state)
        self.assertNotIn("last_alert_fingerprint", self.state)
        self.assertTrue(guardian.WARN)
