"""Local, synthetic-only integration. No network, dynamic code or live credentials."""
import json, hashlib
from pathlib import Path
from prototype import Assistant
from ledger import Ledger

# Trusted code defines the only executable procedures. Stored skill metadata cannot grant authority.
SKILLS = {'briefing': 'prepare morning briefing', 'appointment': 'track appointment', 'bill': 'track bill'}
KINDS = {'inquiry_sent','reply_received','reported_complete','user_confirmed','reopened'}
class Engine:
    def __init__(self, directory):
        p=Path(directory); p.mkdir(mode=0o700,exist_ok=True)
        self.a=Assistant(p/'assistant.db'); self.l=Ledger(p/'evidence.db')
        self.a.db.executescript('''CREATE TABLE IF NOT EXISTS executions(id TEXT PRIMARY KEY, skill TEXT, due TEXT, plan TEXT); CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY, execution TEXT, useful INTEGER);''')
    def close(self): self.a.close(); self.l.close()
    def start(self, skill, occurrence, due):
        if skill not in SKILLS or not isinstance(occurrence,str) or not occurrence or len(occurrence)>128: raise ValueError('invalid skill or occurrence')
        due=self.l.stamp(due)
        eid=hashlib.sha256(json.dumps([skill,occurrence]).encode()).hexdigest()
        # Explicit occurrence identity prevents repeating a recurring goal under the same ID.
        with self.a.db:
            old=self.a.db.execute('SELECT skill,due,plan FROM executions WHERE id=?',(eid,)).fetchone()
            if old and old[:2]!=(skill,due): raise ValueError('execution conflict')
            if not old:
                self.a.db.execute('INSERT INTO executions VALUES(?,?,?,?)',(eid,skill,due,SKILLS[skill]))
        # Idempotent recovery if interrupted between the two SQLite writes.
        self.l.add(eid,due)
        return eid
    def _get(self,eid):
        row=self.a.db.execute('SELECT skill,due,plan FROM executions WHERE id=?',(eid,)).fetchone()
        if not row or SKILLS.get(row[0])!=row[2]: raise ValueError('unknown or altered execution')
        self.l.add(eid,row[1]); return row
    def run(self,eid,fixtures,now):
        skill,due,plan=self._get(eid); now=self.l.stamp(now)
        # Isolate per-occurrence scripted task state; no arbitrary code or external effects.
        local=Assistant(Path(self.a.db.execute('PRAGMA database_list').fetchone()[2]).parent/(eid+'.db'))
        try:
            gid=local.submit(plan)
            safe={k:v for k,v in fixtures.items() if k in ('calendar','bills','packages')}
            # Confirmation booleans in external content never grant completion authority.
            if skill!='briefing': safe[{'appointment':'appointment_confirmation','bill':'payment_confirmation'}[skill]]=self.l.status(eid,now)=='confirmed'
            result=local.run(gid,safe)
            # The briefing artifact itself is the completion evidence for that narrow task.
            if skill=='briefing' and result['status']=='complete':
                self.l.record(eid,eid+':artifact','reported_complete',due if now>=due else now) if not self.l.db.execute('SELECT 1 FROM evidence WHERE id=?',(eid+':artifact',)).fetchone() else None
            return {'execution':eid,'tasks':result['tasks'],'state':self.l.status(eid,now),'notice':self.l.notify(eid,now)}
        finally: local.close()
    def evidence(self,eid,token,kind,stamp,source):
        self._get(eid)
        # Source is a trusted test harness argument, NOT a security/authentication boundary.
        if kind not in KINDS or source not in ('synthetic_provider','synthetic_user'): raise ValueError('invalid evidence')
        if kind in ('user_confirmed','reopened') and source!='synthetic_user': raise PermissionError('confirmation requires user')
        return self.l.record(eid,token,kind,stamp)
    def feedback(self,eid,token,useful):
        self._get(eid)
        if type(useful) is not bool: raise ValueError('boolean required')
        with self.a.db:
            old=self.a.db.execute('SELECT execution,useful FROM feedback WHERE id=?',(token,)).fetchone()
            if old and old!=(eid,int(useful)): raise ValueError('feedback conflict')
            self.a.db.execute('INSERT OR IGNORE INTO feedback VALUES(?,?,?)',(token,eid,int(useful)))
    def skill_stats(self):
        return dict((s,{'ratings':n,'positive':p or 0}) for s,n,p in self.a.db.execute('SELECT e.skill,COUNT(f.id),SUM(f.useful) FROM executions e LEFT JOIN feedback f ON e.id=f.execution GROUP BY e.skill'))
