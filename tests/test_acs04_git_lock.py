"""ACS-04 Git lock evidence and safe-removal regression checks."""
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from agents.infrastructure_guardian import Config, InfrastructureGuardian

class GitLockChecks(unittest.TestCase):
    def create_guardian(self, root, apply=False):
        root = Path(root)
        (root / ".git").mkdir(exist_ok=True)
        return InfrastructureGuardian(Config(repo_root=root, memory_root=root / "memory",
            state_dir=root / "state", quota_bytes=10**9), apply_repairs=apply)

    def test_recent_lock_is_normal_activity(self):
        with tempfile.TemporaryDirectory() as d:
            g = self.create_guardian(d, apply=True)
            lock = Path(d) / ".git/index.lock"
            lock.write_text("active")
            with patch.object(g, "git_processes", return_value=[]):
                g.check_git_lock()
            self.assertEqual(g.findings[-1].severity, "healthy")
            self.assertEqual(g.findings[-1].code, "GIT_LOCK_ACTIVE")
            self.assertTrue(lock.exists())

    def test_old_orphaned_lock_is_critical_in_read_only_mode(self):
        with tempfile.TemporaryDirectory() as d:
            g = self.create_guardian(d, apply=False)
            lock = Path(d) / ".git/index.lock"
            lock.write_text("orphan")
            old = time.time() - 601
            os.utime(lock, (old, old))
            with patch.object(g, "git_processes", return_value=[]):
                g.check_git_lock()
            self.assertEqual(g.findings[-1].severity, "critical")
            self.assertEqual(g.findings[-1].code, "GIT_INDEX_LOCK")
            self.assertTrue(lock.exists())

    def test_old_lock_with_live_git_process_not_removed(self):
        with tempfile.TemporaryDirectory() as d:
            g = self.create_guardian(d, apply=True)
            lock = Path(d) / ".git/index.lock"
            lock.write_text("busy")
            old = time.time() - 601
            os.utime(lock, (old, old))
            with patch.object(g, "git_processes", return_value=["123 git status"]):
                g.check_git_lock()
            self.assertEqual(g.findings[-1].severity, "healthy")
            self.assertTrue(lock.exists())

if __name__ == "__main__":
    unittest.main()
