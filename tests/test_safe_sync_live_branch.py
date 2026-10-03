from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from agents import safe_sync_live_branch as sync


class SafeSyncLiveBranchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.remote = root / "remote.git"
        self.writer = root / "writer"
        self.live = root / "live"

        self.git(root, "init", "--bare", str(self.remote))
        self.git(root, "clone", str(self.remote), str(self.writer))
        self.git(self.writer, "config", "user.email", "acs-test@example.invalid")
        self.git(self.writer, "config", "user.name", "ACS Test")
        self.git(self.writer, "checkout", "-b", "v1.1-dev")

        (self.writer / "agents").mkdir(parents=True)
        (self.writer / "memory" / "logs").mkdir(parents=True)
        (self.writer / "agents" / "example.py").write_text("version = 1\n")
        (self.writer / "memory" / "logs" / "runtime.log").write_text("base\n")
        self.git(self.writer, "add", ".")
        self.git(self.writer, "commit", "-m", "initial")
        self.git(self.writer, "push", "-u", "origin", "v1.1-dev")

        self.git(root, "clone", "--branch", "v1.1-dev", str(self.remote), str(self.live))
        self.git(self.live, "config", "user.email", "acs-test@example.invalid")
        self.git(self.live, "config", "user.name", "ACS Test")

        sync.REPO = self.live
        sync.BRANCH = "v1.1-dev"
        sync.REMOTE = "origin/v1.1-dev"

    def tearDown(self):
        self.temp.cleanup()

    def git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(
                f"git {' '.join(args)} failed in {cwd}: "
                f"{result.stderr or result.stdout}"
            )
        return result

    def advance_remote(self, value: int = 2):
        (self.writer / "agents" / "example.py").write_text(f"version = {value}\n")
        self.git(self.writer, "add", "agents/example.py")
        self.git(self.writer, "commit", "-m", f"remote version {value}")
        self.git(self.writer, "push", "origin", "v1.1-dev")

    def run_sync(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = sync.main()
        payload = json.loads(output.getvalue().strip().splitlines()[-1])
        return rc, payload

    def test_fast_forward_preserves_runtime_churn(self):
        self.advance_remote()
        runtime = self.live / "memory" / "logs" / "runtime.log"
        runtime.write_text("live runtime state\n")

        rc, payload = self.run_sync()

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["behind_after"], 0)
        self.assertEqual(runtime.read_text(), "live runtime state\n")
        self.assertEqual((self.live / "agents" / "example.py").read_text(), "version = 2\n")

    def test_copied_forward_remote_source_bootstraps_safely(self):
        self.advance_remote()

        # Recreate the production bootstrap condition: a launcher copied the
        # newest source file into an older checkout while HEAD stayed behind.
        remote_text = (self.writer / "agents" / "example.py").read_text()
        (self.live / "agents" / "example.py").write_text(remote_text)

        rc, payload = self.run_sync()

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["behind_after"], 0)
        self.assertEqual((self.live / "agents" / "example.py").read_text(), remote_text)
        status = self.git(self.live, "status", "--porcelain=v1", "-uno").stdout
        self.assertNotIn("agents/example.py", status)

    def test_arbitrary_local_source_edit_blocks_without_overwrite(self):
        self.advance_remote()
        source = self.live / "agents" / "example.py"
        source.write_text("LOCAL IMPORTANT EDIT\n")
        before = self.git(self.live, "rev-parse", "HEAD").stdout.strip()

        rc, payload = self.run_sync()

        self.assertEqual(rc, 2)
        self.assertEqual(payload["status"], "blocked_local_source_changes")
        self.assertIn("agents/example.py", payload["unsafe_paths"])
        self.assertEqual(source.read_text(), "LOCAL IMPORTANT EDIT\n")
        after = self.git(self.live, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(before, after)

    def test_local_commit_blocks_automatic_sync(self):
        source = self.live / "agents" / "local_only.py"
        source.write_text("local = True\n")
        self.git(self.live, "add", "agents/local_only.py")
        self.git(self.live, "commit", "-m", "local commit")
        self.advance_remote()

        rc, payload = self.run_sync()

        self.assertEqual(rc, 2)
        self.assertEqual(payload["status"], "local_commits_present")

    def test_already_synced_runtime_churn_does_not_create_stash(self):
        runtime = self.live / "memory" / "logs" / "runtime.log"
        runtime.write_text("changed while synced\n")
        before = self.git(self.live, "stash", "list").stdout

        rc, payload = self.run_sync()

        after = self.git(self.live, "stash", "list").stdout
        self.assertEqual(rc, 0)
        self.assertEqual(payload["status"], "already_synced")
        self.assertEqual(before, after)
        self.assertEqual(runtime.read_text(), "changed while synced\n")


if __name__ == "__main__":
    unittest.main()
