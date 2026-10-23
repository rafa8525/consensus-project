"""Safety-gate regression checks; no access to live runtime required."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/"tools"/"acs_repair_gate_20261023.py"
spec=importlib.util.spec_from_file_location("acs_repair_gate", SCRIPT)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class SafetyGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.prev=gate.ROOT
        gate.ROOT=self.root
        self.git("init")
        self.git("config","user.email","test@example.invalid")
        self.git("config","user.name","ACS Test")
        self.git("checkout","-b","v1.1-dev")
        (self.root/"memory"/"agents").mkdir(parents=True)
        (self.root/"agents").mkdir()
        (self.root/"tools").mkdir()
        (self.root/"agents"/"supervisor.py").write_text("x=1\n")
        self.git("add",".")
        self.git("commit","-m","base")
    def tearDown(self):
        gate.ROOT=self.prev
        self.temp.cleanup()
    def git(self,*args):
        p=subprocess.run(["git",*args],cwd=self.root,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        return p
    def test_runtime_churn_not_source_change(self):
        p=self.root/"memory"/"agents"/"state.json"
        p.write_text('{"ok":true}\n')
        self.git("add",".")
        self.git("commit","-m","track baseline state")
        p.write_text('{"ok":false}\n')
        x=gate.classify()
        self.assertIn("memory/agents/state.json",x["runtime_modified"])
        self.assertEqual(x["source_modified"],[])
    def test_new_python_code_flagged(self):
        p=self.root/"tools"/"unreviewed.py"
        p.write_text("print(1)\n")
        x=gate.classify()
        self.assertIn("tools/unreviewed.py",x["source_untracked"])
    def test_backup_candidate_kept(self):
        p=self.root/"agents"/"supervisor.py.pre-20261023"
        p.write_text("important backup")
        x=gate.classify()
        self.assertIn("agents/supervisor.py.pre-20261023",x["backup_candidates"])
        self.assertTrue(p.exists())
    def test_stale_cycle_is_not_healthy(self):
        from datetime import datetime,timezone,timedelta
        old=(datetime.now(timezone.utc)-timedelta(hours=50)).isoformat()
        p=self.root/"memory"/"agents"/"acs02_state.json"
        p.write_text(json.dumps({"status":"healthy","finished_at_utc":old}))
        self.assertFalse(gate.agent_state("ACS-02")["healthy"])
    def test_missing_cycle_fails_closed(self):
        self.assertFalse(gate.agent_state("ACS-05")["healthy"])
    def test_malformed_cycle_fails_closed(self):
        p=self.root/"memory"/"agents"/"acs03_state.json"
        p.write_text("{broken")
        self.assertFalse(gate.agent_state("ACS-03")["healthy"])

if __name__=="__main__": unittest.main()
