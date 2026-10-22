"""Regression tests for canonical Gmail and snapshot monitoring."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import core_monitors_bundle as monitor

class GmailHealthTests(unittest.TestCase):
    def check_log(self, data, age=10):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "gmail_refresh_guard.log"
            path.write_text(data)
            with patch.object(monitor, "candidate_paths", return_value=[path]):
                result = monitor.gmail_guard_check(path.stat().st_mtime + age)
            return result.status

    def test_successful_oauth_attempt(self):
        self.assertEqual(self.check_log(
            "2026-10-22T20:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T20:00:01Z ok gmail_api_authenticated account=test@example.invalid\n"), "ok")

    def test_error_does_not_count_as_success(self):
        self.assertEqual(self.check_log(
            "2026-10-22T20:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T20:00:01Z error oauth_credentials_invalid\n"), "warn")

    def test_incomplete_run_not_success(self):
        self.assertEqual(self.check_log(
            "2026-10-22T19:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T19:00:01Z ok gmail_api_authenticated account=test@example.invalid\n"
            "2026-10-22T20:00:00Z start gmail_refresh_guard\n"), "warn")

    def test_recovered_run_passes(self):
        self.assertEqual(self.check_log(
            "2026-10-22T19:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T19:00:01Z error oauth_credentials_invalid\n"
            "2026-10-22T20:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T20:00:01Z ok gmail_api_authenticated account=test@example.invalid\n"), "ok")

    def test_stale_run_fails(self):
        self.assertEqual(self.check_log(
            "2026-10-22T20:00:00Z start gmail_refresh_guard\n"
            "2026-10-22T20:00:01Z ok gmail_api_authenticated account=test@example.invalid\n",
            age=monitor.MAX_AGE_S + 10), "warn")

    def test_missing_log_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(monitor, "candidate_paths", return_value=[Path(d) / "none.log"]):
                self.assertEqual(monitor.gmail_guard_check(10000).status, "warn")

    def test_unhealthy_aggregate(self):
        self.assertEqual(monitor.overall_status([
            monitor.CheckResult("gmail", "warn", "failed")]), "warn")

if __name__ == "__main__":
    unittest.main()
