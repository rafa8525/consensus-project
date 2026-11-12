"""Safety and lifecycle tests for the opt-in ACS incident journal."""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agents.acs_incident_coordinator import load, request_repair, update


class IncidentJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "incidents.json"
        self.now = datetime(2026, 10, 27, tzinfo=timezone.utc)
        self.evidence = (self.now - timedelta(minutes=1)).isoformat()

    def record(self):
        return update(self.path, "ACS-05", "PREDICTION_FEED_WARNING",
                      "warning", self.evidence, now=self.now)

    def test_records_owner_and_reviewer(self):
        incident = self.record()
        self.assertEqual(incident["owner"], "ACS-05")
        self.assertEqual(incident["reviewer"], "ACS-03")
        self.assertEqual(incident["state"], "diagnosis_required")
        self.assertIn("ACS-05:PREDICTION_FEED_WARNING", load(self.path)["incidents"])

    def test_idempotent_repeat(self):
        self.record()
        self.record()
        self.assertEqual(len(load(self.path)["incidents"]), 1)

    def test_rejects_unsafe_action(self):
        self.record()
        with self.assertRaises(ValueError):
            request_repair(self.path, "ACS-05", "PREDICTION_FEED_WARNING",
                           "git_reset_hard", now=self.now)

    def test_proposal_does_not_execute(self):
        self.record()
        incident = request_repair(self.path, "ACS-05",
                                  "PREDICTION_FEED_WARNING",
                                  "retry_idempotent_feed", now=self.now)
        self.assertEqual(incident["state"], "awaiting_simulation_and_review")
        self.assertEqual(incident["last_action"], "proposal_only")
        with self.assertRaises(ValueError):
            request_repair(self.path, "ACS-05", "PREDICTION_FEED_WARNING",
                           "retry_idempotent_feed", now=self.now)

    def test_rejects_future_evidence(self):
        with self.assertRaises(ValueError):
            update(self.path, "ACS-04", "WORKTREE_DIRTY", "warning",
                   (self.now + timedelta(hours=1)).isoformat(), now=self.now)

    def test_rejects_malformed_incident_code(self):
        with self.assertRaises(ValueError):
            update(self.path, "ACS-04", "../secret", "warning",
                   self.evidence, now=self.now)


if __name__ == "__main__":
    unittest.main()
