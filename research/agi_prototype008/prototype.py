"""Offline demonstrator: fixed intent routing, synthetic adapters, durable SQLite.
No network, credentials, external effects or live AI agents."""
import sqlite3,json,hashlib
class Assistant:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS goals(id TEXT PRIMARY KEY, objective TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS tasks(goal TEXT, action TEXT, status TEXT, attempts INTEGER DEFAULT 0, evidence TEXT, PRIMARY KEY(goal,action));
        CREATE TABLE IF NOT EXISTS memory(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS notices(key TEXT PRIMARY KEY,body TEXT);''')
    def close(self): self.db.close()
    def remember(self,key,value):
        with self.db:self.db.execute('INSERT OR REPLACE INTO memory VALUES(?,?)',(key,json.dumps(value)))
    def recall(self,key,default=None):
        row=self.db.execute('SELECT value FROM memory WHERE key=?',(key,)).fetchone();return json.loads(row[0]) if row else default
    def submit(self,objective):
        # Exact intent allowlist: never interpret arbitrary instructions as authority.
        plans={'prepare morning briefing':['calendar','bills','packages','briefing'],
               'morning briefing':['calendar','bills','packages','briefing'],
               'track appointment':['calendar','appointment_confirmation'],
               'track bill':['bills','payment_confirmation'],
               'pay bill':['bills','payment_confirmation','external_action']}
        if objective.strip().lower() not in plans:raise ValueError('unsupported objective; no execution')
        actions=plans[objective.strip().lower()]
        gid=hashlib.sha256(objective.encode()).hexdigest()[:24]
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO goals VALUES(?,?,?)',(gid,objective,'pending'))
            for a in actions:self.db.execute('INSERT OR IGNORE INTO tasks(goal,action,status) VALUES(?,?,?)',(gid,a,'pending'))
        return gid
    def notice(self,key,body):
        with self.db:return self.db.execute('INSERT OR IGNORE INTO notices VALUES(?,?)',(key,body)).rowcount==1
    def run(self,gid,fixtures):
        if not self.db.execute('SELECT 1 FROM goals WHERE id=?',(gid,)).fetchone():raise ValueError('unknown goal')
        for a,s,n in self.db.execute('SELECT action,status,attempts FROM tasks WHERE goal=? ORDER BY rowid',(gid,)).fetchall():
            if s=='verified':continue
            if a=='external_action': status,evidence='blocked','external effects disabled; approval plus adapter required'
            elif a=='briefing':
                prior=self.db.execute('SELECT action,status,evidence FROM tasks WHERE goal=? AND action IN (\'calendar\',\'bills\',\'packages\')',(gid,)).fetchall()
                if len(prior)==3 and all(r[1]=='verified' for r in prior):
                    status,evidence='verified',json.dumps({r[0]:json.loads(r[2]) for r in prior});self.notice(gid+':briefing',evidence)
                else: status,evidence='waiting','sources incomplete'
            elif a.endswith('_confirmation'):
                if fixtures.get(a) is True:status,evidence='verified','synthetic confirmation supplied'
                else: status,evidence='waiting','no completion evidence';self.notice(gid+':'+a,'Follow-up required')
            else:
                value=fixtures.get(a)
                if n>=2 and s=='failed':continue
                if value is None:status,evidence='failed','synthetic adapter unavailable'
                else:status,evidence='verified',json.dumps(value)
            with self.db:self.db.execute('UPDATE tasks SET status=?,attempts=attempts+1,evidence=? WHERE goal=? AND action=?',(status,evidence,gid,a))
        rows=self.db.execute('SELECT action,status,attempts,evidence FROM tasks WHERE goal=? ORDER BY rowid',(gid,)).fetchall()
        status='complete' if all(r[1]=='verified' for r in rows) else 'open'
        with self.db:self.db.execute('UPDATE goals SET status=? WHERE id=?',(status,gid))
        return {'goal':gid,'status':status,'tasks':[dict(zip(('action','status','attempts','evidence'),r)) for r in rows]}
    def opportunities(self,fixtures):
        limit=self.recall('max_questions',3)
        return [x for x in fixtures.get('opportunities',[]) if isinstance(x,str)][:max(0,min(3,int(limit)))]
