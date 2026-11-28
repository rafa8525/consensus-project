"""Review candidate. Real transport is gated; tests inject a fake transport."""
import os,json,urllib.request, pathlib
from live_preflight import request_body,validate_response,MODEL

def validate_gate(e):
    checks={'GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_REPOSITORY':'rafa8525/consensus-project','GITHUB_REF':'refs/heads/research/agi-iteration-001-20261119','GITHUB_RUN_ATTEMPT':'1','AGI_APPROVAL':'YES-PROTOTYPE-008','AGI_FINANCIAL_VERIFICATION':'VERIFIED','AGI_ALLOWED_MODEL':MODEL}
    if any(e.get(k)!=v for k,v in checks.items()): raise PermissionError('gate failed')
    if not e.get('GITHUB_RUN_ID','').isdigit() or e.get('GITHUB_RUN_ID')!=e.get('AGI_AUTHORIZED_RUN_ID'): raise PermissionError('run binding failed')
    if not e.get('OPENAI_API_KEY') or not e.get('OPENAI_PROJECT_ID'): raise PermissionError('credential/project missing')

def transport(body,e):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): return None
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+e['OPENAI_API_KEY'],'OpenAI-Project':e['OPENAI_PROJECT_ID'],'Content-Type':'application/json'},method='POST')
    with opener.open(req,timeout=30) as r:
        raw=r.read(65537)
    if len(raw)>65536: raise ValueError('response too large')
    return json.loads(raw)

def execute(e,marker,send):
    validate_gate(e)
    # Consume before transmission, including ambiguous timeout. Never retry.
    with open(marker,'x') as f: f.write(e['GITHUB_RUN_ID'])
    response=send(request_body(),e)
    if response.get('status')!='completed': raise ValueError('response not completed')
    items=response.get('output',[])
    if any(i.get('type') not in ('reasoning','message') for i in items): raise ValueError('unexpected output')
    content=[c for i in items if i.get('type')=='message' for c in i.get('content',[])]
    if len(content)!=1 or content[0].get('type')!='output_text': raise ValueError('unexpected content')
    skills=validate_response(content[0]['text'])
    return {'status':'plan_validated','skills':skills,'objectives_completed':False,'usage':{k:v for k,v in response.get('usage',{}).items() if k in ('input_tokens','output_tokens','total_tokens') and type(v) is int}}

if __name__=='__main__':
    try: print(json.dumps(execute(os.environ,pathlib.Path(os.environ['RUNNER_TEMP'])/'agi008-consumed',transport)))
    except Exception: raise SystemExit('Preflight or request failed; no retry; reconcile usage before any further authorization')
