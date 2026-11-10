"""Isolated regression tests for ACS-05 log rotation; no production writes."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agents import continuity_guardian_agent as guardian


class ContinuityLogRotationTests(unittest.TestCase):
    def test_rotates_at_limit_and_preserves_recent_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            log = root / "continuity.log"
            log.write_text("a" * 80)
            with patch.object(guardian, "LOG", log), patch.object(guardian, "SYSLOG", root), patch.object(guardian, "MAX_LOG_BYTES", 100):
                guardian.log("first message forces rotation")
                self.assertLess(log.stat().st_size, 100)
                self.assertEqual((root / "continuity.log.1").stat().st_size, 80)
                # Fill and rotate again.
                log.write_text("b" * 85)
                guardian.log("second message forces rotation")
                self.assertEqual((root / "continuity.log.2").stat().st_size, 80)
                self.assertEqual((root / "continuity.log.1").stat().st_size, 85)
                self.assertLess(log.stat().st_size, 100)

    def test_does_not_touch_historical_forensic_archives(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            log = root / "continuity.log"
            forensic = root / "continuity.log.archive.20261110T221720Z"
            forensic.write_text("forensic contents")
            log.write_text("x" * 80)
            with patch.object(guardian, "LOG", log), patch.object(guardian, "SYSLOG", root), patch.object(guardian, "MAX_LOG_BYTES", 100):
                guardian.log("rotate")
            self.assertEqual(forensic.read_text(), "forensic contents")

    def test_short_message_appended_without_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            log = root / "continuity.log"
            with patch.object(guardian, "LOG", log), patch.object(guardian, "SYSLOG", root):
                guardian.log("diagnostic")
            self.assertIn("diagnostic", log.read_text())
            self.assertFalse((root / "continuity.log.1").exists())


if __name__ == "__main__":
    unittest.main()
