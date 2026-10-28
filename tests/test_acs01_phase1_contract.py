"""Regression contracts for ACS-01 Phase 1 architecture.

Run from repository root:
    python3 -m unittest discover -s tests -p 'test_acs01_phase1_contract.py'
No credentials, scheduled runs, or network requests required.
"""
import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "agents" / "supervisor.py"
LAUNCHER = ROOT / "agents" / "run_acs01_supervisor.sh"


class PhaseOneContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SUPERVISOR.read_text(encoding="utf-8")
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_launcher_is_only_sync_owner(self):
        self.assertIn('export ACS01_BRANCH_SYNC_RC="$SYNC_RC"', self.launcher)
        self.assertIn('python3 "$TMP_SYNC"', self.launcher)
        self.assertNotIn("_safe_fast_forward_live_branch", self.source)
        self.assertNotIn('subprocess.run(["git"', self.source)

    def test_launcher_evidence_fails_closed(self):
        klass = next(n for n in self.tree.body
                     if isinstance(n, ast.ClassDef) and n.name == "Supervisor")
        method = next(n for n in klass.body
                      if isinstance(n, ast.FunctionDef)
                      and n.name == "_launcher_sync_evidence")
        source = ast.unparse(method)
        scope = {"os": os, "Dict": dict, "Any": object}
        exec(source, scope)
        inspect = scope["_launcher_sync_evidence"]
        cases = [
            (None, False, "launcher_evidence_missing"),
            ("bad", False, "launcher_evidence_invalid"),
            ("3", False, "launcher_sync_failed"),
            ("0", True, "launcher_sync_ok"),
        ]
        for value, expected_ok, expected_status in cases:
            with self.subTest(value=value):
                settings = {} if value is None else {"ACS01_BRANCH_SYNC_RC": value}
                with patch.dict(os.environ, settings, clear=True):
                    result = inspect(None)
                self.assertEqual(result["ok"], expected_ok)
                self.assertEqual(result["status"], expected_status)

    def test_child_agent_json_parser_is_imported(self):
        imported = {
            alias.name
            for node in self.tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertIn("json", imported)
        self.assertIn("json.loads(line)", self.source)

    def test_scheduler_requires_aggregate_health(self):
        self.assertIn('system_health.get("ok") is True', self.source)
        self.assertIn('system_healthy and bridge.get("ok") is True', self.source)
        self.assertIn('st["last_supervisor_status"]', self.source)
        self.assertIn('st["last_system_status"]', self.source)


if __name__ == "__main__":
    unittest.main()
