"""ACS-05 verifies authoritative scheduled supervisor evidence, not legacy MCL log.

Offline fixtures; no production credentials or host writes.
"""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from agents import continuity_guardian_agent as g

NOW = datetime(2026, 11, 19, 18, 3, 9, tzinfo=timezone.utc)


class ScheduledSupervisorEvidenceTests(unittest.TestCase):
    def setUp(self):
        g.CRITICAL.clear()
        g.WARN.clear()
        g.INFO.clear()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.state = self.root / "memory" / "agents" / "state.json"
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.clock = patch.object(g, "now_utc", return_value=NOW)
        self.base = patch.object(g, "BASE", self.root)
        self.clock.start()
        self.base.start()
        self.addCleanup(self.clock.stop)
        self.addCleanup(self.base.stop)
        self.addCleanup(g.CRITICAL.clear)
        self.addCleanup(g.WARN.clear)
        self.addCleanup(g.INFO.clear)

    def record(self, age_seconds=60, status="ok"):
        self.state.write_text(json.dumps({
            "last_supervisor_ts": NOW.timestamp() - age_seconds,
            "last_supervisor_status": status,
            "last_system_status": "degraded",
        }))

    def test_recent_supervisor_core_healthy_even_if_dependency_degraded(self):
        self.record()
        g.check_master_control()
        self.assertEqual(g.CRITICAL, [])
        self.assertEqual(g.WARN, [])
        self.assertTrue(any("fresh verified core" in s for s in g.INFO))

    def test_legacy_log_does_not_override_fresh_supervisor(self):
        self.record()
        legacy = self.root / "memory" / "logs" / "system" / "master_control_loop.log"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text("obsolete legacy cycle success more than 48h ago")
        g.check_master_control()
        self.assertEqual(g.CRITICAL, [])

    def test_stale(self):
        self.record(age_seconds=129601)
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_future_timestamp_rejected(self):
        self.record(age_seconds=-301)
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_degraded_supervisor_fails_closed(self):
        self.record(status="degraded")
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_missing_state_fails_closed(self):
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_malformed_state_fails_closed(self):
        self.state.write_text("{bad json")
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_missing_timestamp_fails_closed(self):
        self.state.write_text(json.dumps({"last_supervisor_status": "ok"}))
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_boolean_timestamp_fails_closed(self):
        self.state.write_text(json.dumps({"last_supervisor_status": "ok", "last_supervisor_ts": True}))
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)

    def test_supervisor_state_symlink_rejected(self):
        real = self.root / "untrusted_state.json"
        real.write_text(json.dumps({
            "last_supervisor_status": "ok", "last_supervisor_ts": NOW.timestamp()
        }))
        self.state.symlink_to(real)
        g.check_master_control()
        self.assertEqual(len(g.CRITICAL), 1)


if __name__ == "__main__":
    unittest.main()
