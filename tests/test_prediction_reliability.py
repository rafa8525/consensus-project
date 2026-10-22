"""Regression tests for the isolated Prediction Feed repair branch.
Run: python3 -m unittest discover -s tests -p 'test_prediction_reliability.py'
"""
import unittest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from agents.prediction_feed_agent import Context, summarize_health, detect_system_health

class PredictionReliabilityTests(unittest.TestCase):
    def test_future_event_does_not_refresh_old_snapshot(self):
        report = ("# System Health Snapshot\n- Generated: 2026-10-01T12:00:00+00:00\n"
                  "- Next run: 2031-01-01T12:00:00+00:00\n- Overall: ok\n")
        status, generated, *_ = summarize_health(report)
        self.assertEqual(status, "OK")
        self.assertEqual(generated, datetime(2026, 10, 1, 12, tzinfo=timezone.utc))

    def test_unlabelled_timestamp_not_accepted(self):
        _, generated, *_ = summarize_health(
            "Next run: 2031-01-01T12:00:00+00:00\n- Overall: ok")
        self.assertIsNone(generated)

    def test_duplicate_generation_timestamp_rejected(self):
        _, generated, *_ = summarize_health(
            "- Generated: 2026-10-01T12:00:00+00:00\n"
            "- Generated: 2026-10-02T12:00:00+00:00\n- Overall: ok")
        self.assertIsNone(generated)

    def test_stale_ok_report_downgraded_and_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            report = root / "logs/status/system_health_snapshot.md"
            report.parent.mkdir(parents=True)
            report.write_text("- Generated: 2026-10-01T12:00:00+00:00\n- Overall: ok\n")
            ctx = Context(
                now=datetime(2026, 10, 22, 21, tzinfo=timezone.utc),
                repo_root=root / "repo", memory_root=root
            )
            detect_system_health(ctx)
            messages = [finding.message for finding in ctx.findings]
            self.assertTrue(any("System health: WARN" in m for m in messages))
            self.assertTrue(any("Health snapshot is stale" in m for m in messages))

    def test_missing_generation_timestamp_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            report = root / "logs/status/system_health_snapshot.md"
            report.parent.mkdir(parents=True)
            report.write_text("- Overall: ok\nNext run: 2031-01-01T12:00:00+00:00\n")
            ctx = Context(now=datetime.now(timezone.utc), repo_root=root / "repo", memory_root=root)
            detect_system_health(ctx)
            self.assertTrue(any("freshness is unknown or invalid" in f.message for f in ctx.findings))
            self.assertFalse(any("System health: OK" in f.message for f in ctx.findings))

if __name__ == "__main__":
    unittest.main()
