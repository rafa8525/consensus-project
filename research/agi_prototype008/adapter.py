"""Simulated reasoning adapter. No network or live model implementation."""
import json
from planner import Planner

GOALS = frozenset({'overview','appointment_tracking','bill_tracking'})
NEEDS = {'overview': ('briefing', {'calendar','bills','packages'}),
         'appointment_tracking': ('appointment', {'calendar'}),
         'bill_tracking': ('bill', {'bills'})}
class TemporaryProviderError(Exception): pass
class InvalidProposal(ValueError): pass

def unique_pairs(pairs):
    d = {}
    for k,v in pairs:
        if k in d: raise InvalidProposal('duplicate JSON field')
        d[k]=v
    return d

def parse(raw):
    if type(raw) is not str or len(raw)>4096: raise InvalidProposal('response size/type')
    try: obj=json.loads(raw,object_pairs_hook=unique_pairs)
    except (ValueError,RecursionError) as e: raise InvalidProposal('invalid JSON') from e
    if type(obj) is not dict or set(obj)!={'version','goals'} or type(obj['version']) is not int or obj['version']!=1: raise InvalidProposal('schema')
    g=obj['goals']
    if type(g) is not list or not 1<=len(g)<=3 or any(type(x) is not str or x not in GOALS for x in g) or len(set(g))!=len(g): raise InvalidProposal('goals')
    return g

def verify(goals, trusted_scope, permissions, proposed_skills):
    # Separate verifier uses trusted scope, not the model's interpretation of authority.
    if set(goals)!=set(trusted_scope): raise PermissionError('objective scope mismatch')
    expected=[]
    for g in trusted_scope:
        skill,needs=NEEDS[g]
        if not needs<=permissions: raise PermissionError('missing permission')
        expected.append(skill)
    if tuple(sorted(expected))!=tuple(proposed_skills): raise PermissionError('plan mismatch')

class ScriptedProvider:
    def __init__(self, replies): self.replies=iter(replies); self.calls=0
    def propose(self, objective):
        self.calls+=1
        try: r=next(self.replies)
        except StopIteration: raise TemporaryProviderError('fixture exhausted')
        if isinstance(r,Exception): raise r
        return r

class Adapter:
    def __init__(self,path,provider): self.planner=Planner(path); self.provider=provider
    def close(self): self.planner.close()
    def run(self,objective,scope,permissions,occurrence,due,fixtures,now):
        if type(self.provider) is not ScriptedProvider: raise PermissionError('only simulated provider allowed')
        if type(objective) is not str or not objective.strip() or len(objective)>2000: raise ValueError('objective')
        if type(scope) not in (list,tuple) or not scope or any(type(g) is not str or g not in GOALS for g in scope) or len(set(scope))!=len(scope): raise ValueError('trusted scope required')
        permissions=frozenset(permissions)
        if not permissions<={'calendar','bills','packages'}: raise PermissionError('unknown permission')
        for i in range(2):
            try: goals=parse(self.provider.propose(objective)); break
            except (TemporaryProviderError,InvalidProposal):
                if i==1: return {'status':'proposal_failed','attempts':2,'executed':False}
        try:
            _,plan,_=self.planner.plan(goals,permissions)
            verify(goals,scope,permissions,plan)
        except (ValueError,PermissionError): return {'status':'denied','attempts':i+1,'executed':False}
        # No execution retry here: unknown partial effects require reconciliation.
        result=self.planner.run(goals,permissions,occurrence,due,fixtures,now)
        verified=result['procedure_verified'] and tuple(result['plan'])==plan and len(result['results'])==len(plan)
        return {'status':'procedure_verified' if verified else 'incomplete','attempts':i+1,'executed':True,'objectives_confirmed':result['objectives_confirmed'],'result':result}
