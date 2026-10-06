import os
import unittest
from unittest.mock import patch

from agents.prediction_feed_agent import summarize_health


BASE = """# System Health Snapshot
- Generated: 2026-10-06T16:24:00+00:00
| Subsystem | Status | Notes |
|---|---|---|
| absorb_status_report | ok | recent |
| geofence_heartbeat | ok | recent |
| gmail_refresh_guard_v3 | warn | stale (12.2d old): /tmp/gmail_refresh_guard_v3.log |
| movies_monitor | ok | recent |
- Overall: warn
"""


class PredictionFeedHealthTests(unittest.TestCase):
    def test_overall_warn_wins_over_earlier_ok_rows(self):
        status, _, _, _, unexpected, expected = summarize_health(BASE)
        self.assertEqual(status, "WARN")
        self.assertTrue(any("gmail_refresh_guard_v3" in item for item in unexpected))
        self.assertEqual(expected, [])

    def test_all_ok_snapshot_is_ok(self):
        text = BASE.replace(
            "| gmail_refresh_guard_v3 | warn | stale (12.2d old): /tmp/gmail_refresh_guard_v3.log |",
            "| gmail_refresh_guard_v3 | ok | recent |",
        ).replace("- Overall: warn", "- Overall: ok")
        status, _, _, _, unexpected, expected = summarize_health(text)
        self.assertEqual(status, "OK")
        self.assertEqual(unexpected, [])
        self.assertEqual(expected, [])

    def test_expected_stale_is_not_unexpected(self):
        text = BASE.replace("stale (12.2d old)", "expected stale (12.2d old)")
        status, _, _, _, unexpected, expected = summarize_health(text)
        self.assertEqual(status, "WARN")
        self.assertEqual(unexpected, [])
        self.assertTrue(any("gmail_refresh_guard_v3" in item for item in expected))

    def test_expected_component_env_override(self):
        with patch.dict(os.environ, {
            "PREDICTION_EXPECTED_STALE_COMPONENTS": "gmail_refresh_guard_v3"
        }, clear=False):
            status, _, _, _, unexpected, expected = summarize_health(BASE)
        self.assertEqual(status, "WARN")
        self.assertEqual(unexpected, [])
        self.assertTrue(any("gmail_refresh_guard_v3" in item for item in expected))

    def test_hard_error_is_error(self):
        text = BASE.replace(
            "| gmail_refresh_guard_v3 | warn | stale (12.2d old): /tmp/gmail_refresh_guard_v3.log |",
            "| gmail_refresh_guard_v3 | error | missing credential refresh |",
        ).replace("- Overall: warn", "- Overall: error")
        status, _, _, _, unexpected, _ = summarize_health(text)
        self.assertEqual(status, "ERROR")
        self.assertTrue(any("gmail_refresh_guard_v3" in item for item in unexpected))

    def test_missing_overall_derives_warn_from_component(self):
        text = BASE.replace("- Overall: warn\n", "")
        status, _, _, _, unexpected, _ = summarize_health(text)
        self.assertEqual(status, "WARN")
        self.assertTrue(unexpected)


if __name__ == "__main__":
    unittest.main()
