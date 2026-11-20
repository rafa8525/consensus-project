"""Integration tests for the actual model checkpoint and lease queue."""
import json, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path
from leased_worker import connect, setup, enqueue, claim, complete, reclaim_expired, status
from leased_model_worker import run_once
from local_inference import fit, save_checkpoint
ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "agents_registry.json"

class LeasedModelWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.db = self.dir / "tasks.sqlite"
        self.cp = self.dir / "checkpoint.json"
        save_checkpoint(self.cp, fit())
        self.con = connect(self.db)
        self.addCleanup(self.con.close)
        setup(self.con)
    def put(self, tid="t1", agent="AGI-01", objective="design benchmark for a new training approach"):
        enqueue(self.con, tid, agent, "design_experiment", objective)
    def test_real_inference_and_persistence(self):
        self.put()
        result = run_once(self.db, REGISTRY, self.cp, "AGI-01")
        self.assertTrue(result["completed"])
        row=self.con.execute("SELECT result FROM lease_tasks WHERE id='t1'").fetchone()
        self.assertEqual(json.loads(row[0])["result"]["prediction"]["label"], "design_experiment")
        self.assertEqual(status(self.con)[0]["status"], "done")
    def test_no_task_is_noop(self):
        self.assertIsNone(run_once(self.db, REGISTRY, self.cp, "AGI-01"))
    def test_invalid_checkpoint_blocks_claim(self):
        self.put()
        tampered = json.loads(self.cp.read_text())
        tampered["model"]["training_count"] = 999
        self.cp.write_text(json.dumps(tampered))
        with self.assertRaises(ValueError): run_once(self.db, REGISTRY, self.cp, "AGI-01")
        self.assertEqual(status(self.con)[0]["status"], "queued")
    def test_unknown_agent_blocks_claim(self):
        self.put()
        with self.assertRaises(ValueError): run_once(self.db, REGISTRY, self.cp, "AGI-99")
        self.assertEqual(status(self.con)[0]["status"], "queued")
    def test_recover_crashed_claim(self):
        self.put()
        owned=claim(self.con,"AGI-01",seconds=2,now=100)
        self.assertEqual(reclaim_expired(self.con,now=103),1)
        self.assertFalse(complete(self.con,owned,{"production_changed":False,"model_trained_in_this_task":False},now=104))
        result=run_once(self.db,REGISTRY,self.cp,"AGI-01")
        self.assertTrue(result["completed"])
        self.assertEqual(status(self.con)[0]["attempts"],2)
    def test_exhausted_attempts_remain_failed(self):
        self.put()
        claim(self.con,"AGI-01",seconds=2,now=100)
        reclaim_expired(self.con,now=103)
        claim(self.con,"AGI-01",seconds=2,now=104)
        reclaim_expired(self.con,now=107)
        self.assertIsNone(run_once(self.db,REGISTRY,self.cp,"AGI-01"))
        self.assertEqual(status(self.con)[0]["status"],"failed")
    def test_cli_subprocess(self):
        self.put()
        p=subprocess.run([sys.executable,str(ROOT/"leased_model_worker.py"),
            "--db",str(self.db),"--registry",str(REGISTRY),
            "--checkpoint",str(self.cp),"--agent","AGI-01"],
            capture_output=True,text=True,timeout=20,check=True)
        self.assertTrue(json.loads(p.stdout)["completed"])
        self.assertEqual(status(self.con)[0]["status"],"done")

if __name__=="__main__":unittest.main()
