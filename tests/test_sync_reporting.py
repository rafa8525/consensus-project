"""Safe-sync reporting regression tests (all git operations mocked)."""
import contextlib
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents import safe_sync_live_branch as sync


def response(stdout="", returncode=0):
    return SimpleNamespace(stdout=stdout, stderr="", returncode=returncode)


def fake_run(*args, **kwargs):
    if args[:3] == ("git", "branch", "--show-current"):
        return response("v1.1-dev\n")
    if args[:2] == ("git", "fetch"):
        return response()
    if args[:3] == ("git", "rev-parse", "--short"):
        return response("abcdef1\n")
    raise AssertionError("Unexpected git operation: " + repr(args))


def exercise(runtime, source, ahead=0, behind=0):
    output = io.StringIO()
    with patch.object(sync, "run", side_effect=fake_run), \
         patch.object(sync, "divergence", return_value=(ahead, behind)), \
         patch.object(sync, "classify_changes", return_value=(runtime, source)), \
         contextlib.redirect_stdout(output):
        code = sync.main()
    return code, json.loads(output.getvalue().strip().splitlines()[-1])


class SyncReportingTests(unittest.TestCase):
    def test_clean_already_synced(self):
        code, data = exercise([], [])
        self.assertEqual(code, 0)
        self.assertTrue(data["worktree_clean"])
        self.assertFalse(data["local_source_changes_present"])
        self.assertEqual(data["status"], "already_synced")

    def test_dirty_source_already_synced(self):
        code, data = exercise([], ["agents/example.py"])
        self.assertEqual(code, 0)
        self.assertEqual(data["status"], "already_synced")
        self.assertTrue(data["local_source_changes_present"])
        self.assertFalse(data["worktree_clean"])
        self.assertEqual(data["local_source_paths"], ["agents/example.py"])

    def test_runtime_changes_already_synced(self):
        code, data = exercise(["memory/agents/state.json"], [])
        self.assertEqual(code, 0)
        self.assertFalse(data["worktree_clean"])
        self.assertFalse(data["local_source_changes_present"])
        self.assertEqual(data["runtime_changes_preserved"], ["memory/agents/state.json"])

    def test_local_commits_still_block(self):
        code, data = exercise([], [], ahead=1)
        self.assertEqual(code, 2)
        self.assertEqual(data["status"], "local_commits_present")

    def test_behind_unsafe_change_still_blocks(self):
        output = io.StringIO()
        with patch.object(sync, "run", side_effect=fake_run), \
             patch.object(sync, "divergence", return_value=(0, 1)), \
             patch.object(sync, "classify_changes", return_value=([], ["agents/example.py"])), \
             patch.object(sync, "blob_sha", return_value="remote"), \
             patch.object(sync, "local_blob_sha", return_value="unverified"), \
             patch.object(sync, "blob_is_from_remote_history", return_value=False), \
             contextlib.redirect_stdout(output):
            code = sync.main()
        data = json.loads(output.getvalue().strip().splitlines()[-1])
        self.assertEqual(code, 2)
        self.assertEqual(data["status"], "blocked_local_source_changes")


if __name__ == "__main__":
    unittest.main()
