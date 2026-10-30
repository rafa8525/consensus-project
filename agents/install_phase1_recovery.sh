#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
import os, sys, json, ast, subprocess, urllib.request
home=Path.home()
repo=home/'consensus-project'
launch=repo/'agents/run_pythonanywhere_health_bridge.sh'
dest=home/'.config/ai-consensus'
runner=dest/'recovery_watchdog.py'
backup=dest/'original_health_schedule.json'
if not launch.is_file(): raise SystemExit('ERROR: bridge launcher missing, schedule unchanged')
token=os.getenv('API_TOKEN')
user=os.getenv('USER')
if not token or not user or not user.replace('_','').isalnum(): raise SystemExit('ERROR: PythonAnywhere credentials unavailable')
code=r'''#!/usr/bin/env python3
import json, subprocess, sys, time, urllib.request
from pathlib import Path
from datetime import datetime,timezone
repo=Path.home()/'consensus-project'
launch=repo/'agents/run_pythonanywhere_health_bridge.sh'
log=Path.home()/'.local/state/ai-consensus/recovery.jsonl'
url='https://raw.githubusercontent.com/rafa8525/consensus-project/main/logs/system/pythonanywhere_health.json'
names=['ACS-01','ACS-02','ACS-03','ACS-04','ACS-05']
def write(event,**kw):
    log.parent.mkdir(parents=True,exist_ok=True)
    record={'at':datetime.now(timezone.utc).isoformat(),'event':event,**kw}
    with log.open('a') as f:f.write(json.dumps(record)+'\\n')
    print(json.dumps(record),flush=True)
def validate(j):
    bad=[]
    try:
        dt=datetime.fromisoformat(j['generated_at_utc'].replace('Z','+00:00'))
        if dt.tzinfo is None or not 0<=(datetime.now(timezone.utc)-dt).total_seconds()<1800:bad.append('report_stale')
    except (ValueError,TypeError,KeyError):bad.append('timestamp_invalid')
    for n in names:
        v=(j.get('agents') or {}).get(n) or {}
        if v.get('verified') is not True or v.get('status')!='current' or v.get('health_status') not in ('ok','healthy'):
            bad.append(n+'_unhealthy')
    tasks=j.get('pythonanywhere_schedule') or {}
    if not tasks.get('available') or not all((tasks.get(k) or {}).get('enabled') for k in ('health_task','acs01_task')):
        bad.append('scheduler_problem')
    sync=(j.get('self_heal') or {}).get('branch_sync') or {}
    if not sync.get('ok') or sync.get('ahead_after')!=0 or sync.get('behind_after')!=0:
        bad.append('sync_failure')
    cycles=(j.get('self_heal') or {}).get('post_sync_cycles') or {}
    for n in ('ACS-04','ACS-05'):
        if not any(x.get('ok') for x in ((cycles.get('outcomes') or {}).get(n) or [])):bad.append(n+'_cycle_failure')
    return bad
def execute(cmd,timeout=1200):
    try:return subprocess.run(cmd,cwd=repo,timeout=timeout,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    except (OSError,subprocess.TimeoutExpired):return False
def read():
    request=urllib.request.Request(url+'?t='+str(int(time.time())),headers={'User-Agent':'ACS-Watchdog'})
    with urllib.request.urlopen(request,timeout=35) as r:return json.load(r)
def main():
    if '--self-test' in sys.argv:
        j={'generated_at_utc':datetime.now(timezone.utc).isoformat(),
           'agents':{n:{'verified':True,'status':'current','health_status':'healthy'} for n in names},
           'pythonanywhere_schedule':{'available':True,'health_task':{'enabled':True},'acs01_task':{'enabled':True}},
           'self_heal':{'branch_sync':{'ok':True,'ahead_after':0,'behind_after':0},'post_sync_cycles':{'outcomes':{'ACS-04':[{'ok':True}],'ACS-05':[{'ok':True}]}}}}
        assert validate(j)==[]
        j['agents']['ACS-03']['status']='stale';assert validate(j)
        j['agents']['ACS-03']['status']='current';j['self_heal']['branch_sync']['behind_after']=1;assert validate(j)
        print('PASS: fault-decision self-tests');return 0
    for i in range(1,4):
        ok=execute(['bash',str(launch)],1200)
        try:j=read();errors=validate(j)
        except Exception:j={};errors=['public_report_unavailable']
        if ok and not errors:write('healthy',attempt=i);return 0
        write('recovery_needed',attempt=i,launcher_ok=ok,issues=errors)
        if i<3:
            for n in names[1:]:
                v=(j.get('agents') or {}).get(n) or {}
                if v.get('status')!='current' or v.get('health_status')!='healthy':
                    repaired=execute([sys.executable,str(repo/'agents/run_acs_cycle.py'),n],600)
                    write('agent_retry',agent=n,ok=repaired)
            time.sleep(i*10)
    write('escalation',reason='automatic_retries_exhausted');return 2
if __name__=='__main__':sys.exit(main())
'''
ast.parse(code)
dest.mkdir(parents=True,exist_ok=True)
runner.write_text(code)
runner.chmod(0o700)
p=subprocess.run([sys.executable,str(runner),'--self-test'],capture_output=True,text=True)
print(p.stdout.strip())
if p.returncode:raise SystemExit('ERROR: self-test failed; schedule unchanged')
base=f'https://www.pythonanywhere.com/api/v0/user/{user}/schedule/'
def api(uri,method='GET',payload=None):
    h={'Authorization':f'Token {token}'}
    if payload is not None:h['Content-Type']='application/json'
    r=urllib.request.Request(uri,headers=h,data=json.dumps(payload).encode() if payload is not None else None,method=method)
    with urllib.request.urlopen(r,timeout=30) as response:return json.load(response)
tasks=api(base)
match=[x for x in tasks if x.get('id')==1521711 or 'run_pythonanywhere_health_bridge.sh' in str(x.get('command',''))]
if len(match)!=1:raise SystemExit('ERROR: health schedule not uniquely identified; unchanged')
task=match[0]
oldcmd=str(task.get('command',''))
if not any(k in oldcmd for k in ('run_pythonanywhere_health_bridge.sh','recovery_watchdog.py')):
    raise SystemExit('ERROR: schedule command differs; unchanged')
if task.get('enabled') is not True:raise SystemExit('ERROR: health task disabled; unchanged')
if not backup.exists():
    backup.write_text(json.dumps({'id':task['id'],'command':oldcmd},indent=2))
    backup.chmod(0o600)
elif json.loads(backup.read_text()).get('id')!=task['id']:
    raise SystemExit('ERROR: backup task ID mismatch')
newcmd=f'python3 {runner}'
if oldcmd!=newcmd:api(base+str(task['id'])+'/','PATCH',{'command':newcmd})
verified=api(base+str(task['id'])+'/')
if verified.get('command')!=newcmd or verified.get('enabled') is not True:
    api(base+str(task['id'])+'/','PATCH',{'command':oldcmd})
    raise SystemExit('ERROR: failed verification; old schedule restored')
print('INSTALLED: health task protected by 3 bounded retries and evidence validation')
print('Log:',Path.home()/'.local/state/ai-consensus/recovery.jsonl')
print('Note: a future unattended failure must be observed to prove real self-recovery.')
PY
