import json, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path
from worker_runtime import connect, setup, load_registry, enqueue, run_once, snapshot
HERE=Path(__file__).parent
class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/"test.sqlite"
        self.con=connect(self.db)
        self.addCleanup(self.con.close)
        setup(self.con)
        self.roles=load_registry(HERE/"agents_registry.json")
    def t(self,tid,agent,op="design_experiment",deps=None):
        return {"id":tid,"agent_id":agent,"operation":op,"objective":"Bounded research objective","dependencies":deps or []}
    def test_registry(self): self.assertEqual(len(self.roles),55)
    def test_worker_claim_once(self):
        enqueue(self.con,self.roles,self.t("a","AGI-01"))
        self.assertEqual(run_once(self.con,self.roles,"AGI-01","w1")["task_id"],"a")
        self.assertIsNone(run_once(self.con,self.roles,"AGI-01","w2"))
    def test_dependencies_and_messages(self):
        enqueue(self.con,self.roles,self.t("a","AGI-01"))
        enqueue(self.con,self.roles,self.t("b","AGI-17","review_hypothesis",["a"]))
        self.assertIsNone(run_once(self.con,self.roles,"AGI-17","w17"))
        run_once(self.con,self.roles,"AGI-01","w1")
        self.assertEqual(run_once(self.con,self.roles,"AGI-17","w17")["dependency_receipts"][0]["task_id"],"a")
        self.assertEqual(len(snapshot(self.con)["messages"]),2)
    def test_bad_operation_rejected(self):
        with self.assertRaises(ValueError): enqueue(self.con,self.roles,self.t("x","AGI-01","shell"))
    def test_unknown_agent_rejected(self):
        with self.assertRaises(ValueError): enqueue(self.con,self.roles,self.t("x","AGI-99"))
    def test_missing_dependency_rejected(self):
        with self.assertRaises(ValueError): enqueue(self.con,self.roles,self.t("x","AGI-01",deps=["missing"]))
    def test_task_cap(self):
        for i in range(55): enqueue(self.con,self.roles,self.t(f"t{i}","AGI-01"))
        with self.assertRaises(ValueError): enqueue(self.con,self.roles,self.t("overflow","AGI-01"))
    def test_two_real_processes(self):
        for agent,tid in [("AGI-01","a"),("AGI-02","b")]: enqueue(self.con,self.roles,self.t(tid,agent))
        procs=[subprocess.Popen([sys.executable,str(HERE/"worker_runtime.py"),"--db",str(self.db),"--registry",
              str(HERE/"agents_registry.json"),"worker-once","--agent",agent,"--worker-id",agent],
              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for agent in ("AGI-01","AGI-02")]
        for p in procs:
            out,err=p.communicate(timeout=10)
            self.assertEqual(p.returncode,0,err)
            self.assertIn("digest",out)
        self.assertEqual([x["status"] for x in snapshot(self.con)["tasks"]],["done","done"])
    def test_persistence(self):
        enqueue(self.con,self.roles,self.t("a","AGI-01"))
        run_once(self.con,self.roles,"AGI-01","w")
        other=connect(self.db)
        try: self.assertEqual(snapshot(other)["tasks"][0]["status"],"done")
        finally: other.close()
    def test_duplicate_rejected(self):
        enqueue(self.con,self.roles,self.t("a","AGI-01"))
        with self.assertRaises(sqlite3.IntegrityError): enqueue(self.con,self.roles,self.t("a","AGI-01"))
if __name__=="__main__": unittest.main()
