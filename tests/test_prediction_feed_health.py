import os
import unittest
from unittest.mock import patch

from datetime import datetime, timezone
from pathlib import Path

from agents.prediction_feed_agent import Context, Finding, add_predictions, summarize_health


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


    def test_expected_warn_does_not_emit_degraded_prediction(self):
        ctx = Context(
            now=datetime(2026, 10, 6, 16, 24, tzinfo=timezone.utc),
            repo_root=Path("/tmp/repo"),
            memory_root=Path("/tmp/memory"),
        )
        ctx.findings.append(Finding(
            "System/Project",
            "MEDIUM",
            "System health: WARN (1 minutes old). Details: Expected warning(s): maintenance_guard: warn (expected dormant)",
            "Expected maintenance window.",
            "No corrective action required; all warning components are explicitly marked expected/dormant.",
        ))
        add_predictions(ctx)
        messages = [
            finding.message
            for finding in ctx.findings
            if finding.section == "24–72 Hour Predictions"
        ]
        self.assertNotIn(
            "Prediction quality may remain degraded until the upstream health warning is cleared.",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
