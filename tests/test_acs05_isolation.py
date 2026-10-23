"""ACS-05 reentrancy and current-cycle finding regression tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agents import continuity_guardian_agent as g

class ContinuityIsolationTests(unittest.TestCase):
    def setUp(self):
        g.CRITICAL.clear()
        g.WARN.clear()
        g.INFO.clear()
    def tearDown(self):
        g.CRITICAL.clear()
        g.WARN.clear()
        g.INFO.clear()

    def test_repeated_findings_deduplicated_and_notified_once(self):
        state = {}
        saved = []
        sms = []
        def repeated():
            g.CRITICAL.extend(["token failed"] * 201 + ["infra failed"] * 82)
            g.WARN.extend(["resource warning"] * 531)
        with patch.object(g, "load_state", return_value=state), \
             patch.object(g, "save_state", side_effect=lambda data: saved.append(dict(data))), \
             patch.object(g, "maybe_send_sms", side_effect=lambda *args: sms.append(args)), \
             patch.object(g, "check_google_oauth", side_effect=repeated), \
             patch.object(g, "check_gmail_wiring"), \
             patch.object(g, "check_master_control"), \
             patch.object(g, "check_memory_compressor"), \
             patch.object(g, "check_absorption_and_prediction"), \
             patch.object(g, "check_resource_pressure"), \
             patch.object(g, "check_vpn_simulation"), \
             patch.object(g, "log"):
            result = g._run_unlocked(force=True)
        self.assertEqual(result, 2)
        self.assertEqual(saved[0]["critical"], ["token failed", "infra failed"])
        self.assertEqual(saved[0]["warnings"], ["resource warning"])
        self.assertEqual(len(sms), 1)

    def test_overlapping_run_fails_closed_without_running_checks(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(g, "LOCK", Path(d) / "guardian.lock"), \
                 patch.object(g.fcntl, "flock", side_effect=BlockingIOError), \
                 patch.object(g, "_run_unlocked") as check, \
                 patch.object(g, "log"):
                self.assertEqual(g.run(), 2)
                check.assert_not_called()

    def test_new_cycle_replaces_historical_findings(self):
        old = {"last_status": "CRITICAL", "critical": ["old token revoked"] * 201, "warnings": ["old warning"] * 531}
        saved = []
        with patch.object(g, "load_state", return_value=old), \
             patch.object(g, "save_state", side_effect=lambda data: saved.append(dict(data))), \
             patch.object(g, "maybe_send_sms"), \
             patch.object(g, "check_google_oauth"), \
             patch.object(g, "check_gmail_wiring"), \
             patch.object(g, "check_master_control"), \
             patch.object(g, "check_memory_compressor"), \
             patch.object(g, "check_absorption_and_prediction"), \
             patch.object(g, "check_resource_pressure"), \
             patch.object(g, "check_vpn_simulation"), \
             patch.object(g, "log"):
            self.assertEqual(g._run_unlocked(force=True), 0)
        self.assertEqual(saved[0]["critical"], [])
        self.assertEqual(saved[0]["warnings"], [])
        self.assertEqual(saved[0]["last_status"], "OK")

if __name__ == "__main__":
    unittest.main()
