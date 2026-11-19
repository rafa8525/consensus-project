"""Fault-injection tests for cross-agent published incident ingestion."""
import unittest
from agents.acs_incident_ingest import collect


class IngestionTests(unittest.TestCase):
    def report(self):
        return {
            "generated_at_utc": "2026-10-27T07:03:53+00:00",
            "agents": {f"ACS-{n:02d}": {
                "verified": True, "status": "current", "health_status": "healthy"
            } for n in range(1, 6)},
            "pythonanywhere_schedule": {
                "acs01_task": {"found": True, "enabled": True},
                "health_task": {"found": True, "enabled": True},
            },
        }

    def test_healthy_report_no_incidents(self):
        self.assertEqual(collect(self.report()), [])

    def test_cross_agent_handoff(self):
        data = self.report()
        data["agents"]["ACS-01"]["status"] = "degraded"
        data["agents"]["ACS-04"].update({
            "status": "degraded", "health_status": "warning",
            "diagnostics": {"findings": [{"code": "WORKTREE_DIRTY", "repaired": False, "severity": "warning"}]}
        })
        data["agents"]["ACS-05"].update({
            "status": "degraded", "health_status": "warning",
            "diagnostics": {"issue_codes": ["PREDICTION_FEED_WARNING", "ALERT_DELIVERY_WARNING"]}
        })
        events = collect(data)
        self.assertIn("ACS-04:WORKTREE_DIRTY", [a + ":" + b for a,b,_,_ in events])
        self.assertIn("ACS-05:ALERT_DELIVERY_WARNING", [a + ":" + b for a,b,_,_ in events])
        self.assertIn("ACS-01:AGENT_HEALTH_DEGRADED", [a + ":" + b for a,b,_,_ in events])

    def test_disabled_scheduler_is_incident(self):
        data = self.report()
        data["pythonanywhere_schedule"]["health_task"]["enabled"] = False
        self.assertIn("SCHEDULE_HEALTH_TASK_UNAVAILABLE", [x[1] for x in collect(data)])

    def test_bad_timestamp_fails_closed(self):
        data = self.report()
        data["generated_at_utc"] = "not-a-timestamp"
        with self.assertRaises(ValueError):
            collect(data)


if __name__ == "__main__":
    unittest.main()
