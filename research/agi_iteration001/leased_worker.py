"""Research-only SQLite worker leases. No production deployment or external effects."""
import hashlib,json,sqlite3,time,uuid
from pathlib import Path
MAX_TASKS=55
MAX_ATTEMPTS=2
OPERATIONS=frozenset(('design_experiment','evaluate_evidence','review_hypothesis'))
def connect(path):
    p=Path(path)
    if not p.parent.is_dir(): raise ValueError('Missing database directory')
    c=sqlite3.connect(str(p),timeout=10,isolation_level=None)
    c.execute('PRAGMA busy_timeout=10000')
    c.execute('PRAGMA journal_mode=WAL')
    return c
def setup(c):
    c.executescript("""
    CREATE TABLE IF NOT EXISTS lease_tasks(
      id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, operation TEXT NOT NULL,
      objective TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('queued','running','done','failed')),
      attempts INTEGER NOT NULL DEFAULT 0, token TEXT, expires REAL, result TEXT);
    CREATE TABLE IF NOT EXISTS lease_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, kind TEXT NOT NULL,
      token TEXT, at REAL NOT NULL, detail TEXT NOT NULL);
    """)
def _agent(a):
    return isinstance(a,str) and len(a)==6 and a.startswith('AGI-') and a[4:].isdigit() and 1<=int(a[4:])<=55
def _duration(seconds):
    if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not 2<=seconds<=300:
        raise ValueError('Lease duration must be 2-300 seconds')
def _event(c,tid,kind,token,at,detail):
    c.execute('INSERT INTO lease_events(task_id,kind,token,at,detail) VALUES(?,?,?,?,?)',(tid,kind,token,at,detail))
def enqueue(c,tid,agent,operation,objective):
    if not isinstance(tid,str) or not tid.isascii() or not 1<=len(tid)<=50 or not all(x.isalnum() or x in '_-' for x in tid): raise ValueError('Bad task ID')
    if not _agent(agent) or operation not in OPERATIONS: raise ValueError('Bad agent or operation')
    if not isinstance(objective,str) or not 0<len(objective.strip())<=500: raise ValueError('Bad objective')
    c.execute('BEGIN IMMEDIATE')
    try:
        if c.execute('SELECT COUNT(*) FROM lease_tasks').fetchone()[0]>=MAX_TASKS: raise ValueError('Queue at capacity')
        c.execute('INSERT INTO lease_tasks(id,agent_id,operation,objective,status) VALUES(?,?,?,?,?)',(tid,agent,operation,objective.strip(),'queued'))
        c.execute('COMMIT')
    except BaseException:
        c.execute('ROLLBACK')
        raise
def reclaim_expired(c,now=None):
    t=time.time() if now is None else float(now)
    c.execute('BEGIN IMMEDIATE')
    try:
        rows=c.execute("SELECT id,attempts,token FROM lease_tasks WHERE status='running' AND expires<=?",(t,)).fetchall()
        for tid,n,token in rows:
            next_status='failed' if n>=MAX_ATTEMPTS else 'queued'
            c.execute('UPDATE lease_tasks SET status=?,token=NULL,expires=NULL WHERE id=?',(next_status,tid))
            _event(c,tid,'lease_expired',token,t,next_status)
        c.execute('COMMIT')
        return len(rows)
    except BaseException:
        c.execute('ROLLBACK')
        raise
def claim(c,agent,seconds=30,now=None):
    if not _agent(agent): raise ValueError('Bad agent ID')
    _duration(seconds)
    t=time.time() if now is None else float(now)
    c.execute('BEGIN IMMEDIATE')
    try:
        row=c.execute("SELECT id,operation,objective,attempts FROM lease_tasks WHERE status='queued' AND agent_id=? ORDER BY id LIMIT 1",(agent,)).fetchone()
        if row is None:
            c.execute('COMMIT')
            return None
        tid,operation,objective,n=row
        token=uuid.uuid4().hex
        c.execute("UPDATE lease_tasks SET status='running',attempts=?,token=?,expires=? WHERE id=? AND status='queued'",(n+1,token,t+seconds,tid))
        _event(c,tid,'claimed',token,t,str(n+1))
        c.execute('COMMIT')
        return {'task_id':tid,'agent_id':agent,'operation':operation,'objective':objective,'token':token,'attempt':n+1}
    except BaseException:
        c.execute('ROLLBACK')
        raise
def heartbeat(c,tid,token,seconds=30,now=None):
    _duration(seconds)
    t=time.time() if now is None else float(now)
    c.execute('BEGIN IMMEDIATE')
    try:
        count=c.execute("UPDATE lease_tasks SET expires=? WHERE id=? AND token=? AND status='running' AND expires>?",(t+seconds,tid,token,t)).rowcount
        if count: _event(c,tid,'heartbeat',token,t,'extended')
        c.execute('COMMIT')
        return count==1
    except BaseException:
        c.execute('ROLLBACK')
        raise
def complete(c,owned,result,now=None):
    if not isinstance(result,dict) or result.get('production_changed') is not False or result.get('model_trained_in_this_task') is not False: raise ValueError('Unsafe result')
    serialized=json.dumps(result,sort_keys=True,separators=(',',':'))
    if len(serialized.encode())>20000: raise ValueError('Result too large')
    digest=hashlib.sha256(serialized.encode()).hexdigest()
    wrapped=json.dumps({'result':result,'digest':digest},sort_keys=True)
    t=time.time() if now is None else float(now)
    c.execute('BEGIN IMMEDIATE')
    try:
        count=c.execute("UPDATE lease_tasks SET status='done',result=?,token=NULL,expires=NULL WHERE id=? AND token=? AND status='running' AND expires>?",(wrapped,owned['task_id'],owned['token'],t)).rowcount
        if count: _event(c,owned['task_id'],'completed',owned['token'],t,digest)
        c.execute('COMMIT')
        return count==1
    except BaseException:
        c.execute('ROLLBACK')
        raise
def model_job(owned,checkpoint,predictor):
    prediction=predictor(checkpoint['model'],owned['objective'])
    if prediction['label'] not in OPERATIONS: raise ValueError('Disallowed prediction')
    return {'operation':owned['operation'],'prediction':prediction,
            'prediction_matches_assignment':owned['operation']==prediction['label'],
            'checkpoint_sha256':checkpoint['sha256'],'agent_id':owned['agent_id'],
            'model_trained_in_this_task':False,'production_changed':False,
            'mode':'BOUNDED_OFFLINE_INFERENCE'}
def status(c):
    return [{'id':tid,'status':state,'attempts':n} for tid,state,n in c.execute('SELECT id,status,attempts FROM lease_tasks ORDER BY id')]
