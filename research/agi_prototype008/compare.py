"""Exploratory comparison: in-chat authored proposals, not an autonomous LLM adapter."""
import json,tempfile
from planner import Planner
from pathlib import Path
D='2026-12-01T12:00:00+00:00'
def evaluate(cases,proposals):
 out=[]
 for i,((utterance,expected,permissions),proposal) in enumerate(zip(cases,proposals)):
  row={'case':i+1,'expected':expected}
  for name,goals in [('structured_direct',utterance),('chat_proposal',proposal)]:
   with tempfile.TemporaryDirectory() as tmp:
    p=Planner(tmp)
    try:
     if goals is None: result=None
     else:
      r=p.run(goals,permissions,'case',D,{k:[] for k in permissions},D)
      result=sorted(goals) if r['procedure_verified'] else 'execution_failed'
    except (ValueError,PermissionError): result=None
    finally:p.close()
   row[name]=result;row[name+'_correct']=result==(sorted(expected) if expected else None)
  out.append(row)
 return out
if __name__=='__main__':
 cases=json.loads(Path('cases.json').read_text()); proposals=json.loads(Path('proposals.json').read_text()); assert len(cases)==len(proposals)
 rows=evaluate(cases,proposals); print(json.dumps({'rows':rows,'scores':{k:sum(r[k+'_correct'] for r in rows) for k in ['structured_direct','chat_proposal']},'n':len(rows)},indent=2))
