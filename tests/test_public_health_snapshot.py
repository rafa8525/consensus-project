"""Ensure public PythonAnywhere snapshots contain no private diagnostics."""
import ast
import json
import unittest
from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[1] / "agents/pythonanywhere_health_bridge.py"
tree = ast.parse(BRIDGE.read_text(encoding="utf-8"))
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in ("public_diagnostics", "sanitize_public_snapshot")]
ns = {}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(BRIDGE), "exec"), ns)
sanitize = ns["sanitize_public_snapshot"]


class PublicHealthSnapshotTests(unittest.TestCase):
    def sample(self):
        secret = "VERY_PRIVATE_CANARY_987"
        return {
            "schema_version": 6, "generated_at_utc": "2026-10-11T18:02:16+00:00",
            "source": "pythonanywhere", "active_branch": "v1.1-dev",
            "agents": {
                "ACS-01": {"verified": True, "health_status": "degraded",
                           "status": "degraded", "email": secret},
                "ACS-05": {"verified": True, "health_status": "critical",
                           "status": "degraded", "diagnostics": {
                               "last_status": "CRITICAL",
                               "critical": ["Google OAuth invalid_grant " + secret],
                               "warnings": ["email subject: " + secret],
                               "diagnostics_source": "/secret/" + secret,
                           }},
                "ACS-04": {"verified": True, "health_status": "warning",
                           "status": "degraded", "diagnostics": {
                               "overall_status": "warning",
                               "findings": [{"severity": "warning", "code": "OVERSIZED_LOGS",
                                             "message": "Private " + secret,
                                             "repair_message": secret, "repaired": False}]}},
            },
            "self_heal": {"branch_sync": {"ok": True, "status": "already_synced",
                                          "stderr": secret},
                          "post_sync_cycles": {"attempted": True,
                                               "outcomes": {"ACS-05": [
                                                   {"ok": False, "returncode": 2,
                                                    "stdout": secret, "stderr": secret}
                                               ]}}},
            "git": {"status": {"ok": True, "returncode": 0,
                               "stdout": "M confidential/" + secret},
                    "last_commit": {"ok": True, "stdout": "a" * 40 + "|" + secret},
                    "origin_reachable": {"ok": True, "stdout": secret}},
            "pythonanywhere_schedule": {
                "available": True,
                "acs01_task": {"found": True, "enabled": True},
                "health_task": {"found": True, "enabled": True},
                "tasks": [{"description": secret}],
            },
            "knowledge_validation": {"status": "ok", "details": secret},
        }, secret

    def test_all_secret_canaries_removed(self):
        private, secret = self.sample()
        public = sanitize(private)
        self.assertNotIn(secret, json.dumps(public))
        self.assertEqual(public["agents"]["ACS-05"]["diagnostics"]["issue_codes"],
                         ["GOOGLE_OAUTH_INVALID_GRANT"])
        self.assertEqual(public["agents"]["ACS-04"]["diagnostics"]["findings"][0]["code"],
                         "OVERSIZED_LOGS")

    def test_health_fields_remain_actionable(self):
        private, _ = self.sample()
        public = sanitize(private)
        self.assertEqual(public["agents"]["ACS-01"]["health_status"], "degraded")
        self.assertEqual(public["agents"]["ACS-05"]["health_status"], "critical")
        self.assertEqual(public["git"]["last_commit"]["sha"], "a" * 40)
        self.assertEqual(public["git"]["status"]["tracked_changes_count"], 1)
        self.assertTrue(public["pythonanywhere_schedule"]["acs01_task"]["enabled"])

    def test_unexpected_diagnostic_is_not_reflected(self):
        private, secret = self.sample()
        private["agents"]["ACS-05"]["diagnostics"] = {"unexpected": secret}
        self.assertNotIn(secret, json.dumps(sanitize(private)))


if __name__ == "__main__":
    unittest.main()
