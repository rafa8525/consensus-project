"""Sandbox-only real subprocess workers using a durable SQLite message queue.
Workers are deterministic research-template executors, NOT independent LLM agents.
"""
import argparse, hashlib, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

OPERATIONS = {
    "review_hypothesis": ["State falsifiable hypothesis", "Identify confounders", "Request independent review"],
    "design_experiment": ["Specify baseline", "Pre-register held-out evaluation", "Define budget and stop rules"],
    "evaluate_evidence": ["Check dataset separation", "Verify repeatability", "Report limitations"],
}
def now(): return datetime.now(timezone.utc).isoformat()
def connect(path):
    con = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    con.execute("PRAGMA busy_timeout=10000")
    con.execute("PRAGMA journal_mode=WAL")
    return con
def setup(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, operation TEXT NOT NULL,
      objective TEXT NOT NULL, dependencies TEXT NOT NULL, status TEXT NOT NULL
      CHECK(status IN ('queued','running','done','failed')), attempts INTEGER NOT NULL DEFAULT 0,
      worker TEXT, created_at TEXT NOT NULL, finished_at TEXT, result_json TEXT);
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, sender TEXT NOT NULL,
      receiver TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
def load_registry(path):
    agents = json.loads(Path(path).read_text(encoding="utf-8"))["agents"]
    if len(agents) != 55 or len({a["id"] for a in agents}) != 55:
        raise ValueError("Expected 55 unique role definitions")
    if any(a.get("production_enabled") is not False or a.get("status") != "PROPOSED_UNVERIFIED" for a in agents):
        raise ValueError("Production enabled or unverified registry state")
    return {a["id"]: a for a in agents}
def enqueue(con, registry, task):
    if not isinstance(task, dict) or set(task) != {"id","agent_id","operation","objective","dependencies"}:
        raise ValueError("Unsupported task fields")
    tid, agent, operation, objective, deps = (task[k] for k in ("id","agent_id","operation","objective","dependencies"))
    if not isinstance(tid,str) or not tid.isascii() or not 1 <= len(tid) <= 50 or not all(c.isalnum() or c in "_-" for c in tid):
        raise ValueError("Invalid task ID")
    if agent not in registry or operation not in OPERATIONS: raise ValueError("Agent/operation not authorized")
    if not isinstance(objective,str) or not 0 < len(objective.strip()) <= 500: raise ValueError("Invalid objective")
    if not isinstance(deps,list) or len(deps)>5 or len(set(deps))!=len(deps) or any(not isinstance(d,str) or d==tid for d in deps):
        raise ValueError("Invalid dependencies")
    con.execute("BEGIN IMMEDIATE")
    try:
        if con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] >= 55: raise ValueError("Task cap reached")
        for dep in deps:
            if not con.execute("SELECT 1 FROM tasks WHERE id=?",(dep,)).fetchone(): raise ValueError("Missing dependency")
        con.execute("INSERT INTO tasks(id,agent_id,operation,objective,dependencies,status,created_at) VALUES(?,?,?,?,?,?,?)",
                    (tid,agent,operation,objective.strip(),json.dumps(deps),"queued",now()))
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise
def claim(con, agent_id, worker_id):
    con.execute("BEGIN IMMEDIATE")
    try:
        rows = con.execute("SELECT id,operation,objective,dependencies FROM tasks WHERE agent_id=? AND status='queued' ORDER BY created_at,id",(agent_id,)).fetchall()
        item = None
        for row in rows:
            if all(con.execute("SELECT status FROM tasks WHERE id=?",(d,)).fetchone()==("done",) for d in json.loads(row[3])):
                item=row
                break
        if item:
            con.execute("UPDATE tasks SET status='running',attempts=attempts+1,worker=? WHERE id=?",(worker_id,item[0]))
        con.execute("COMMIT")
        return item
    except BaseException:
        con.execute("ROLLBACK")
        raise
def run_once(con,registry,agent_id,worker_id):
    if agent_id not in registry or not isinstance(worker_id,str) or not 0<len(worker_id)<=80: raise ValueError("Invalid worker")
    item=claim(con,agent_id,worker_id)
    if item is None: return None
    tid,operation,objective,dep_json=item
    try:
        receipts=[]
        for dep in json.loads(dep_json):
            row=con.execute("SELECT result_json FROM tasks WHERE id=? AND status='done'",(dep,)).fetchone()
            if row is None: raise ValueError("Dependency no longer complete")
            receipts.append({"task_id":dep,"digest":json.loads(row[0])["digest"]})
        result={"task_id":tid,"agent_id":agent_id,"agent_name":registry[agent_id]["name"],
                "operation":operation,"objective":objective,"research_checklist":OPERATIONS[operation],
                "dependency_receipts":receipts,"mode":"DETERMINISTIC_WORKER",
                "is_ai_inference":False,"model_trained":False,"production_changed":False}
        result["digest"]=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute("UPDATE tasks SET status='done',finished_at=?,result_json=? WHERE id=? AND status='running' AND worker=?",
                        (now(),json.dumps(result,sort_keys=True),tid,worker_id))
            con.execute("INSERT INTO messages(task_id,sender,receiver,payload,created_at) VALUES(?,?,?,?,?)",
                        (tid,agent_id,"research_collective",json.dumps({"event":"completed","digest":result["digest"]}),now()))
            con.execute("COMMIT")
        except BaseException:
            con.execute("ROLLBACK")
            raise
        return result
    except Exception as exc:
        con.execute("UPDATE tasks SET status='failed',finished_at=?,result_json=? WHERE id=? AND status='running' AND worker=?",
                    (now(),json.dumps({"error":type(exc).__name__}),tid,worker_id))
        raise
def snapshot(con):
    return {"tasks":[{"id":r[0],"agent":r[1],"status":r[2],"attempts":r[3],"result":json.loads(r[4]) if r[4] else None}
                      for r in con.execute("SELECT id,agent_id,status,attempts,result_json FROM tasks ORDER BY id")],
            "messages":[{"task_id":r[0],"sender":r[1],"receiver":r[2],"payload":json.loads(r[3])}
                         for r in con.execute("SELECT task_id,sender,receiver,payload FROM messages ORDER BY id")]}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",required=True)
    ap.add_argument("--registry",default=str(Path(__file__).with_name("agents_registry.json")))
    subs=ap.add_subparsers(dest="cmd",required=True)
    subs.add_parser("init")
    p=subs.add_parser("enqueue");p.add_argument("--task-file",required=True)
    p=subs.add_parser("worker-once");p.add_argument("--agent",required=True);p.add_argument("--worker-id",required=True)
    subs.add_parser("status")
    args=ap.parse_args()
    registry=load_registry(args.registry)
    db=Path(args.db)
    if not db.parent.is_dir(): ap.error("Database directory must exist")
    con=connect(db)
    setup(con)
    if args.cmd=="enqueue":
        f=Path(args.task_file)
        if f.stat().st_size>100000: raise ValueError("Task file too large")
        enqueue(con,registry,json.loads(f.read_text()))
    elif args.cmd=="worker-once":
        print(json.dumps(run_once(con,registry,args.agent,args.worker_id)))
    elif args.cmd=="status": print(json.dumps(snapshot(con),indent=2,sort_keys=True))
    else: print("Database initialized; no workers launched")
    con.close()
if __name__=="__main__": main()
