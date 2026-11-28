"""Offline preparation only. No transport, credential logging or dispatch."""
from adapter import parse, verify, NEEDS
import os
MODEL='gpt-6-luna'
OBJECTIVE='Fictional scenario: Track an outstanding invoice and an upcoming appointment until each is confirmed resolved.'
SCOPE=('appointment_tracking','bill_tracking')
PERMISSIONS=frozenset({'calendar','bills'})

def request_body():
    return {'model':MODEL,'reasoning':{'effort':'low'},'service_tier':'default','input':[{'role':'developer','content':'Return only a JSON object with version 1 and goals array. Allowed goals: overview, appointment_tracking, bill_tracking. No tools or actions.'},{'role':'user','content':OBJECTIVE}], 'max_output_tokens':512,'store':False,'text':{'format':{'type':'json_schema','name':'personal_plan','strict':True,'schema':{'type':'object','properties':{'version':{'type':'integer','enum':[1]},'goals':{'type':'array','items':{'type':'string','enum':['overview','appointment_tracking','bill_tracking']}}},'required':['version','goals'],'additionalProperties':False}}}}

def preflight():
    return {'credential_present':bool(os.environ.get('OPENAI_API_KEY')), 'funding_verified':False,'hard_limit_verified':False,'dispatch_enabled':False,'requests_sent':0}

def validate_response(raw):
    goals=parse(raw)
    skills=tuple(sorted(NEEDS[g][0] for g in goals))
    verify(goals,SCOPE,PERMISSIONS,skills)
    return skills

if __name__=='__main__':
    import json
    print(json.dumps({'preflight':preflight(),'request_preview':request_body()},indent=2))
