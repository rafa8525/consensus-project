"""Offline tests for one-shot read-only Phase 1 evidence inventory."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import phase1_host_evidence_inventory as target


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.manifest = self.root / "manifest.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_manifest_never_claims_success(self):
        data = target.inspect_proofs(self.manifest, self.evidence)
        self.assertEqual(data["manifest"], "missing")
        self.assertTrue(all(x == "absent" for x in data["tests"].values()))

    def test_matching_digest_is_only_inventory(self):
        raw = b"PASS: failure_detection\n"
        artifact = self.evidence / "failure_detection.log"
        artifact.write_bytes(raw)
        self.manifest.write_text(json.dumps({"tests": {
            "failure_detection": {
                "passed": True, "execution_scope": "production",
                "executed_at_utc": "2026-11-13T00:00:00Z",
                "artifact_path": "failure_detection.log",
                "artifact_sha256": hashlib.sha256(raw).hexdigest()
            }
        }}))
        data = target.inspect_proofs(self.manifest, self.evidence)
        item = data["tests"]["failure_detection"]
        self.assertTrue(item["digest_matches"])
        self.assertTrue(item["production_scope_claimed"])
        self.assertFalse(item["independently_verified"])

    def test_invalid_paths_and_tampered_artifacts_rejected(self):
        for filename, expected in (("../escape.log", "missing_or_unsafe_path"),
                                   ("missing.log", "missing_or_unsafe_path")):
            self.manifest.write_text(json.dumps({"tests": {
                "automatic_retry": {"artifact_path": filename, "artifact_sha256": "0"*64}
            }}))
            self.assertEqual(target.inspect_proofs(self.manifest, self.evidence)
                             ["tests"]["automatic_retry"], expected)
        (self.evidence / "data.log").write_text("different")
        self.manifest.write_text(json.dumps({"tests": {
            "automatic_retry": {"artifact_path": "data.log", "artifact_sha256": "0"*64}
        }}))
        self.assertFalse(target.inspect_proofs(self.manifest, self.evidence)
                         ["tests"]["automatic_retry"]["digest_matches"])

    def test_worktree_counts_only_categories(self):
        class Result:
            returncode = 0
            stdout = b" M agents/secret.py\x00 M memory/private.json\x00"
        with patch.object(target.subprocess, "run", return_value=Result()) as run:
            result = target.inspect_worktree(self.root)
        self.assertEqual(result["tracked_changes"], 2)
        self.assertEqual(result["groups"], {"agents": 1, "memory": 1})
        self.assertNotIn("secret", str(result))
        self.assertNotIn("private", str(result))
        self.assertEqual(run.call_args.kwargs["cwd"], self.root)


if __name__ == "__main__":
    unittest.main()
