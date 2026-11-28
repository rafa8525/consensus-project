"""Offline evidence ledger; no external adapters or personal data."""
import sqlite3
from datetime import datetime, timezone
class Ledger:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS goals(id TEXT PRIMARY KEY, due TEXT NOT NULL, state TEXT NOT NULL); CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, goal TEXT NOT NULL, kind TEXT NOT NULL, stamp TEXT NOT NULL); CREATE TABLE IF NOT EXISTS notices(goal TEXT, state TEXT, PRIMARY KEY(goal,state));''')
    def close(self): self.db.close()
    @staticmethod
    def stamp(value):
        d=datetime.fromisoformat(value)
        if d.tzinfo is None: raise ValueError('timezone required')
        return d.astimezone(timezone.utc).isoformat()
    def add(self,goal,due):
        due=self.stamp(due)
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO goals VALUES(?,?,?)',(goal,due,'scheduled'))
            if self.db.execute('SELECT due FROM goals WHERE id=?',(goal,)).fetchone()[0]!=due: raise ValueError('goal conflict')
    def record(self,goal,eid,kind,stamp):
        # Kind is supplied by a trusted adapter in future integration, never message text.
        if kind not in ('inquiry_sent','reply_received','reported_complete','user_confirmed','reopened'): raise ValueError('unsupported evidence')
        stamp=self.stamp(stamp)
        with self.db:
            if not self.db.execute('SELECT 1 FROM goals WHERE id=?',(goal,)).fetchone(): raise ValueError('unknown goal')
            old=self.db.execute('SELECT goal,kind,stamp FROM evidence WHERE id=?',(eid,)).fetchone()
            if old:
                if old!=(goal,kind,stamp): raise ValueError('evidence conflict')
                return False
            self.db.execute('INSERT INTO evidence VALUES(?,?,?,?)',(eid,goal,kind,stamp))
        return True
    def status(self,goal,now):
        now=self.stamp(now)
        row=self.db.execute('SELECT due FROM goals WHERE id=?',(goal,)).fetchone()
        if not row: raise ValueError('unknown goal')
        state='overdue' if now>row[0] else 'scheduled'
        for (kind,) in self.db.execute('SELECT kind FROM evidence WHERE goal=? AND stamp<=? ORDER BY stamp,id',(goal,now)):
            if kind=='reopened': state='awaiting_completion'
            elif state=='confirmed': continue
            elif kind=='user_confirmed': state='confirmed'
            elif kind=='reported_complete': state='reported_complete'
            elif kind=='reply_received' and state!='reported_complete': state='reply_needs_review'
            elif kind=='inquiry_sent' and state not in ('reported_complete','reply_needs_review'): state='awaiting_reply'
        return state
    def notify(self,goal,now):
        state=self.status(goal,now)
        if state=='scheduled': return None
        with self.db:
            old=self.db.execute('SELECT state FROM goals WHERE id=?',(goal,)).fetchone()[0]
            if old==state:return None
            self.db.execute('UPDATE goals SET state=? WHERE id=?',(state,goal))
        return state
