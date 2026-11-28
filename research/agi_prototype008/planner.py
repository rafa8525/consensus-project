"""Bounded composition of trusted read-only synthetic skills; no live actions."""
import sqlite3,json,hashlib
from skills_engine import Engine
# Capability prerequisites are trusted code, never supplied by provider content.
SKILLS={'briefing':(frozenset({'calendar','bills','packages'}),frozenset({'overview'})), 'appointment':(frozenset({'calendar'}),frozenset({'appointment_tracking'})), 'bill':(frozenset({'bills'}),frozenset({'bill_tracking'}))}
VERSION=1
class Planner:
 def __init__(self,path):
  self.engine=Engine(path); self.db=self.engine.a.db
  self.db.execute('CREATE TABLE IF NOT EXISTS recipes (key TEXT PRIMARY KEY, plan TEXT NOT NULL, verified INTEGER NOT NULL)')
 def close(self): self.engine.close()
 def plan(self, goals, permitted):
  if not isinstance(goals,list) or not goals or len(goals)>3 or any(type(g) is not str for g in goals): raise ValueError('invalid structured objective')
  goals=set(goals); permitted=set(permitted)
  if not goals<=set().union(*(v[1] for v in SKILLS.values())): raise ValueError('unsupported goal')
  plan=tuple(sorted(k for k,(needs,provides) in SKILLS.items() if provides&goals and needs<=permitted))
  if not goals<=set().union(*(SKILLS[k][1] for k in plan)): raise PermissionError('missing read permissions')
  key=hashlib.sha256(json.dumps([VERSION,sorted(goals),sorted(permitted)]).encode()).hexdigest()
  old=self.db.execute('SELECT plan,verified FROM recipes WHERE key=?',(key,)).fetchone()
  if old and tuple(json.loads(old[0]))!=plan: raise ValueError('recipe integrity mismatch')
  return key,plan,bool(old and old[1])
 def run(self,goals,permitted,occurrence,due,fixtures,now):
  key,plan,reused=self.plan(goals,permitted)
  results=[]
  for skill in plan:
   eid=self.engine.start(skill,occurrence,due)
   data={k:v for k,v in fixtures.items() if k in SKILLS[skill][0]}
   results.append(self.engine.run(eid,data,now))
  # A successful execution of a tracking procedure is not closure of its underlying objective.
  verified=all(all(t['status']=='verified' for t in r['tasks'] if not t['action'].endswith('_confirmation')) for r in results)
  if verified:
   with self.db:self.db.execute('INSERT OR IGNORE INTO recipes VALUES(?,?,1)',(key,json.dumps(plan)))
  return {'plan':plan,'reused':reused,'procedure_verified':verified,'objectives_confirmed':all(r['state']=='confirmed' for r in results),'results':results}
