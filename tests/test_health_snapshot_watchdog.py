"""Regression tests for independent PythonAnywhere health watchdog."""
import copy
import unittest
from datetime import datetime, timedelta, timezone
from tools.health_snapshot_watchdog import evaluate, AGENTS

NOW = datetime(2026, 10, 11, 20, tzinfo=timezone.utc)


def clean_snapshot():
    return {
        "source": "pythonanywhere",
        "generated_at_utc": NOW.isoformat(),
        "agents": {
            a: {"verified": True, "health_status": "healthy",
                "status": "current", "last_execution_utc": NOW.isoformat()}
            for a in AGENTS
        },
        "pythonanywhere_schedule": {
            "available": True,
            "acs01_task": {"enabled": True},
            "health_task": {"enabled": True},
        },
    }


class WatchdogTests(unittest.TestCase):
    def test_healthy_snapshot_passes(self):
        self.assertEqual(evaluate(clean_snapshot(), NOW), [])

    def test_degraded_acs01_detected_even_when_fresh(self):
        data = clean_snapshot()
        data["agents"]["ACS-01"]["health_status"] = "degraded"
        data["agents"]["ACS-01"]["status"] = "degraded"
        self.assertTrue(any("ACS-01" in x for x in evaluate(data, NOW)))

    def test_critical_acs05_detected_even_when_fresh(self):
        data = clean_snapshot()
        data["agents"]["ACS-05"]["health_status"] = "critical"
        self.assertTrue(any("ACS-05" in x for x in evaluate(data, NOW)))

    def test_stale_snapshot_fails(self):
        data = clean_snapshot()
        data["generated_at_utc"] = (NOW - timedelta(hours=40)).isoformat()
        self.assertTrue(any("snapshot is stale" in x for x in evaluate(data, NOW)))

    def test_stale_agent_fails(self):
        data = clean_snapshot()
        data["agents"]["ACS-03"]["last_execution_utc"] = (NOW - timedelta(days=2)).isoformat()
        self.assertTrue(any("ACS-03" in x for x in evaluate(data, NOW)))

    def test_missing_agent_fails(self):
        data = clean_snapshot()
        del data["agents"]["ACS-04"]
        self.assertTrue(any("ACS-04" in x for x in evaluate(data, NOW)))

    def test_unverified_agent_fails(self):
        data = clean_snapshot()
        data["agents"]["ACS-02"]["verified"] = False
        self.assertTrue(any("ACS-02" in x for x in evaluate(data, NOW)))

    def test_disabled_scheduler_fails(self):
        data = clean_snapshot()
        data["pythonanywhere_schedule"]["acs01_task"]["enabled"] = False
        self.assertTrue(any("acs01_task" in x for x in evaluate(data, NOW)))

    def test_future_snapshot_fails(self):
        data = clean_snapshot()
        data["generated_at_utc"] = (NOW + timedelta(hours=3)).isoformat()
        self.assertTrue(evaluate(data, NOW))

    def test_malformed_timestamp_fails(self):
        data = clean_snapshot()
        data["generated_at_utc"] = "not-a-date"
        self.assertTrue(evaluate(data, NOW))

    def test_missing_schedule_fails_closed(self):
        data = clean_snapshot()
        data["pythonanywhere_schedule"] = {"available": False}
        self.assertIn("PythonAnywhere scheduler evidence unavailable", evaluate(data, NOW))

    def test_absent_schedule_fails_closed(self):
        data = clean_snapshot()
        del data["pythonanywhere_schedule"]
        self.assertIn("PythonAnywhere scheduler evidence unavailable", evaluate(data, NOW))


if __name__ == "__main__":
    unittest.main()
