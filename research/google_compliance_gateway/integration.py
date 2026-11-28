"""Synthetic-only integration prototype; no provider SDK, networking or deletion."""
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass
from threading import Lock

ROLES = frozenset(f'AGI-{i:02}' for i in range(1,56))
PRODUCTS = frozenset({'gmail','drive','calendar'})
STORES = frozenset({'ChromaDB','Notion','GitHub','PythonAnywhere'})
SOURCES = frozenset({'independent','cloud_customer','cloud_technical','workspace_user','workspace_technical'})

def aware(t):
    return isinstance(t,datetime) and t.tzinfo is not None and t.utcoffset() is not None

class Ledger:
    """SQLite shared local ledger; initialize explicitly, never recreate on error."""
    @staticmethod
    def initialize(path):
        p=Path(path)
        with p.open('xb'): pass
        db=sqlite3.connect(p)
        try:
            db.execute('CREATE TABLE charges (project TEXT, product TEXT, day TEXT, units INTEGER NOT NULL CHECK(units>0), request TEXT PRIMARY KEY)')
            db.commit()
        finally: db.close()
    def __init__(self,path,cap=4500):
        if type(cap) is not int or not 1<=cap<=4500: raise ValueError('cap')
        self.uri=Path(path).resolve().as_uri()+'?mode=rw'
        self.cap=cap
    def reserve(self,project,product,units,now,request):
        if project!='synthetic-project' or product not in PRODUCTS or type(units) is not int or not 0<units<=self.cap or not aware(now) or not isinstance(request,str) or not request.startswith('synthetic-'):
            return False
        day=now.astimezone(timezone.utc).date().isoformat()
        db=None
        try:
            db=sqlite3.connect(self.uri,uri=True,timeout=2)
            db.execute('BEGIN IMMEDIATE')
            n=db.execute('SELECT COALESCE(SUM(units),0) FROM charges WHERE project=? AND product=? AND day=?',(project,product,day)).fetchone()[0]
            if type(n) is not int or n<0 or n+units>self.cap: return False
            db.execute('INSERT INTO charges VALUES (?,?,?,?,?)',(project,product,day,units,request))
            db.commit()
            return True
        except (sqlite3.Error,OSError):
            return False
        finally:
            if db is not None: db.close()

class MockMCP:
    def __init__(self,ledger):
        self.ledger=ledger
        self.calls=0
    def invoke(self,role,product,units,now,request,*,tier,route,authorized,active,fail=False):
        if role not in ROLES or tier!='standard' or route!='google_mcp' or authorized is not True or active is not True: return 'denied'
        if not self.ledger.reserve('synthetic-project',product,units,now,request): return 'denied'
        self.calls+=1
        # Retain reservation on uncertain failure; never retry or fall back.
        return 'uncertain_stop' if fail else 'synthetic_success'

@dataclass(frozen=True)
class Record:
    sources: frozenset
    acquired: datetime
    deadline: datetime
    grant: str
    rights: bool=False

class MockMemory:
    """Metadata only, in memory. Revocation blocks use, flags removal; no deletion."""
    def __init__(self):
        self.records={}
        self.revoked=set()
        self.lock=Lock()
    def revoke(self,grant):
        with self.lock: self.revoked.add(grant)
    def allowed(self,role,record,action,now):
        if role not in ROLES or not isinstance(record,Record) or not isinstance(record.sources,frozenset) or not record.sources or not record.sources<=SOURCES: return False
        if not all(map(aware,(now,record.acquired,record.deadline))) or not record.acquired<=now<record.deadline: return False
        if not isinstance(record.grant,str) or not record.grant.startswith('synthetic-') or record.grant in self.revoked: return False
        if action not in {'process','cache','durable_memory','train','evaluation_dataset'}: return False
        if record.sources==frozenset({'independent'}): return record.rights is True
        if 'cloud_customer' in record.sources: return False
        return now<record.acquired+timedelta(days=30) and action in {'process','cache'}
    def put(self,role,store,key,record,now,*,durable=True):
        with self.lock:
            if store not in STORES or not isinstance(key,str) or not key.startswith('synthetic-') or (store,key) in self.records: return False
            # All named sinks are treated as durable, regardless of caller preference.
            if not self.allowed(role,record,'durable_memory',now): return False
            self.records[store,key]=record
            return True
    def read(self,role,store,key,now):
        with self.lock:
            record=self.records.get((store,key))
            return record if self.allowed(role,record,'process',now) else None
    def pending_removal(self,now):
        with self.lock:
            return tuple(k for k,r in self.records.items() if not self.allowed('AGI-01',r,'process',now))

def derive(a,b):
    """Conservative lineage: mixed grants require separate review, never reset age."""
    if a.grant!=b.grant: raise ValueError('mixed grant')
    return Record(a.sources|b.sources,min(a.acquired,b.acquired),min(a.deadline,b.deadline),a.grant,a.rights is True and b.rights is True)
