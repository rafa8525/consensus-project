"""Offline read-only ACS operational certification regression tests."""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tools.operational_certification import evaluate

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        root = Path(self.t.name)
        self.repo = root / "repo"
        self.mem = root / "memory"
        self.now = datetime.now(timezone.utc)
        def put(path, data):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data)
        self.put = put
        stamp = self.now.isoformat()
        put(self.repo / "memory/logs/system/master_control_loop.log",
            "[2026-10-23 16:30:00] ==== Master Control Loop Cycle Start ====\n"
            "[2026-10-23 16:30:03] ✅ All subsystems executed successfully.\n"
            "[2026-10-23 16:30:03] ==== Master Control Loop Cycle Complete ====\n")
        put(self.mem / "logs/status/system_health_snapshot.md", f"- Generated: {stamp}\n- Overall: ok\n")
        put(self.mem / "logs/system/infrastructure_guardian_status.json",
            '{"finished_at": "' + stamp + '", "overall_status": "healthy"}')
        put(self.repo / "memory/logs/system/continuity_guardian_state.json",
            '{"last_full_check_utc":"' + stamp + '","last_status":"OK","critical":[],"warnings":[]}')
        put(self.mem / "logs/system/predictions" / f"prediction_feed_{self.now.date().isoformat()}.md",
            "Generated: " + stamp + "\n")
        put(self.repo / "common/twilio_guard.py",
            "TWILIO_SILENCE TWILIO_ENABLE_SEND def send_sms( RATE_PER_MIN")
        put(self.repo / "agents/continuity_guardian_agent.py", "twilio_guard.send_sms(")
    def test_healthy_core_does_not_claim_sms_delivery(self):
        result = evaluate(self.repo, self.mem, self.now)
        self.assertTrue(result["core_certified_now"])
        self.assertFalse(result["sms_delivery_verified"])
        self.assertFalse(result["full_operational_certification"])
    def test_small_future_mtime_skew_is_tolerated(self):
        import os
        p = self.repo / "memory/logs/system/master_control_loop.log"
        os.utime(p, (self.now.timestamp()+15, self.now.timestamp()+15))
        self.assertTrue(evaluate(self.repo, self.mem, self.now)["checks"]["unattended_cycle"]["pass"])
    def test_large_future_mtime_skew_fails(self):
        import os
        p = self.repo / "memory/logs/system/master_control_loop.log"
        os.utime(p, (self.now.timestamp()+180, self.now.timestamp()+180))
        self.assertFalse(evaluate(self.repo, self.mem, self.now)["checks"]["unattended_cycle"]["pass"])
    def test_latest_cycle_failure_overrides_previous_success(self):
        p = self.repo / "memory/logs/system/master_control_loop.log"
        p.write_text(p.read_text() +
          "[2026-10-23 16:45:00] ==== Master Control Loop Cycle Start ====\n"
          "[2026-10-23 16:45:03] ❌ Master Control Loop cycle completed with 1 failed subsystem group(s).\n"
          "[2026-10-23 16:45:03] ==== Master Control Loop Cycle Complete ====\n")
        self.assertFalse(evaluate(self.repo, self.mem, self.now)["core_certified_now"])
    def test_stale_acs04_fails(self):
        p = self.mem / "logs/system/infrastructure_guardian_status.json"
        p.write_text('{"finished_at":"2026-10-01T00:00:00Z","overall_status":"healthy"}')
        self.assertFalse(evaluate(self.repo, self.mem, self.now)["checks"]["acs04"]["pass"])
    def test_stale_snapshot_fails(self):
        p = self.mem / "logs/status/system_health_snapshot.md"
        p.write_text("- Generated: 2026-10-01T00:00:00Z\n- Overall: ok\n")
        self.assertFalse(evaluate(self.repo, self.mem, self.now)["checks"]["health_snapshot"]["pass"])

if __name__ == "__main__":
    unittest.main()
