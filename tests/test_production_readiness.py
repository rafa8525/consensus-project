"""Production preflight state tests. No network or credential contents are used."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools.production_readiness import state_health, build_report


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 10, 11, 20, tzinfo=timezone.utc)

    def test_missing_state_fails_closed(self):
        s = state_health(self.root / "missing.json", self.now)
        self.assertFalse(s["fresh"])
        self.assertEqual(s["status"], "unknown")

    def test_recent_healthy_state(self):
        p = self.root / "state.json"
        p.write_text(json.dumps({"status": "healthy",
                                 "verified": True,
                                 "finished_at_utc": self.now.isoformat()}))
        s = state_health(p, self.now)
        self.assertTrue(s["fresh"])
        self.assertEqual(s["status"], "healthy")

    def test_stale_state_is_not_fresh(self):
        p = self.root / "state.json"
        p.write_text(json.dumps({"status": "healthy", "verified": True,
                                 "finished_at_utc": (self.now - timedelta(days=4)).isoformat()}))
        self.assertFalse(state_health(p, self.now)["fresh"])

    def test_future_state_is_not_fresh(self):
        p = self.root / "state.json"
        p.write_text(json.dumps({"status": "healthy", "verified": True,
                                 "finished_at_utc": (self.now + timedelta(hours=2)).isoformat()}))
        self.assertFalse(state_health(p, self.now)["fresh"])

    def test_preflight_does_not_claim_live_authentication(self):
        report = build_report(repo=self.root, environ={}, now=self.now)
        self.assertFalse(report["ready"])
        self.assertFalse(report["gmail"]["authorization_verified"])
        self.assertFalse(report["twilio"]["delivery_verified"])
        self.assertFalse(report["production_verified"])

if __name__ == "__main__":
    unittest.main()
