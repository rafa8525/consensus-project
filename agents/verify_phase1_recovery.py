#!/usr/bin/env python3
"""Safe isolated fault-injection proof for installed Phase-1 watchdog.
Does not change production schedules, repo files or agent state.
"""
import contextlib
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

path=Path.home()/'.config/ai-consensus/recovery_watchdog.py'
if not path.is_file():
    raise SystemExit('FAIL: installed watchdog missing')

spec=importlib.util.spec_from_file_location('acs_recovery_under_test',path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
agents=['ACS-01','ACS-02','ACS-03','ACS-04','ACS-05']

def healthy_report():
    return {
        'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'agents':{n:{'verified':True,'status':'current','health_status':'healthy'} for n in agents},
        'pythonanywhere_schedule':{'available':True,'acs01_task':{'enabled':True},'health_task':{'enabled':True}},
        'self_heal':{'branch_sync':{'ok':True,'ahead_after':0,'behind_after':0},
            'post_sync_cycles':{'outcomes':{'ACS-04':[{'ok':True}],'ACS-05':[{'ok':True}]}}}
    }

assert mod.validate(healthy_report())==[], 'baseline healthy snapshot rejected'
assert 'report_stale' in mod.validate({**healthy_report(),'generated_at_utc':'2020-01-01T00:00:00+00:00'})
assert 'ACS-03_unhealthy' in mod.validate({**healthy_report(),'agents':{**healthy_report()['agents'],'ACS-03':{'verified':True,'status':'stale','health_status':'healthy'}}})
print('PASS: health and stale-state detection')

original={name:getattr(mod,name) for name in ('execute','read','write')}
old_sleep=mod.time.sleep
old_argv=sys.argv
events=[]

def injected_execute(cmd,timeout=1200):
    # Actually exercise a failing child process, then a successful child.
    if cmd[0]=='bash':
        attempt=sum(1 for e in events if e[0]=='launch')+1
        events.append(('launch',attempt))
        code=17 if attempt==1 else 0
        return subprocess.run([sys.executable,'-c',f'import sys;sys.exit({code})']).returncode==0
    raise AssertionError('Unexpected production agent action in isolated test')

try:
    mod.execute=injected_execute
    mod.read=healthy_report
    mod.write=lambda event,**fields:events.append((event,fields))
    mod.time.sleep=lambda _:None
    sys.argv=[str(path)]
    with contextlib.redirect_stdout(io.StringIO()):
        result=mod.main()
    assert result==0, f'expected recovered exit 0, got {result}'
    assert len([x for x in events if x[0]=='launch'])==2, 'expected two launch attempts'
    assert [x[0] for x in events if x[0] in ('recovery_needed','healthy')]==['recovery_needed','healthy']
    print('PASS: real child-process failure -> automatic retry -> successful recovery')

    events.clear()
    mod.execute=lambda cmd,timeout=1200:False if cmd[0]=='bash' else True
    mod.read=healthy_report
    with contextlib.redirect_stdout(io.StringIO()):
        result=mod.main()
    assert result==2, f'expected escalation exit 2, got {result}'
    assert len([x for x in events if x[0]=='recovery_needed'])==3
    assert events[-1][0]=='escalation'
    print('PASS: persistent failure -> three attempts -> explicit escalation')
finally:
    for name,value in original.items():setattr(mod,name,value)
    mod.time.sleep=old_sleep
    sys.argv=old_argv

if os.environ.get('API_TOKEN') and os.environ.get('USER'):
    try:
        import urllib.request
        user=os.environ['USER']
        request=urllib.request.Request(
            f'https://www.pythonanywhere.com/api/v0/user/{user}/schedule/',
            headers={'Authorization':'Token '+os.environ['API_TOKEN']})
        with urllib.request.urlopen(request,timeout=20) as response:
            tasks=json.load(response)
        matches=[t for t in tasks if t.get('id')==1521711]
        assert len(matches)==1 and matches[0].get('enabled') is True
        assert 'recovery_watchdog.py' in matches[0].get('command','')
        print('PASS: PythonAnywhere scheduled task enabled and wired to recovery watchdog')
    except Exception as exc:
        print('CHECK REQUIRED: schedule API verification unsuccessful:',type(exc).__name__)
        raise SystemExit(2)
else:
    print('CHECK REQUIRED: API_TOKEN/USER unavailable; cannot verify schedule')
    raise SystemExit(2)

print('RESULT: bounded recovery validated safely. Unattended production execution still requires independent scheduled-run evidence.')
