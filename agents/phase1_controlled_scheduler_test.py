#!/usr/bin/env python3
"""Controlled ACS-01 schedule re-enable test; safe simulation by default.
Live test proves API-mediated re-enablement, NOT unattended GitHub recovery.
"""
import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ID=1524414
OUT=Path.home()/'.local/state/ai-consensus/phase1_controlled_scheduler_test.json'
GUARD=Path('/tmp/acs_guard.py')

def imported_guard():
    if not GUARD.is_file():
        raise RuntimeError('guard_missing')
    spec=importlib.util.spec_from_file_location('acs_guard_for_test',GUARD)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def same_config(before,after):
    return isinstance(before,dict) and isinstance(after,dict) and {
        k:v for k,v in before.items() if k!='enabled'
    }=={k:v for k,v in after.items() if k!='enabled'}

def test(mod,token,live=False):
    api=mod.fetch_json
    before=api(mod.API_URL,token=token)
    if mod.validate_task(before) or before['enabled'] is not True:
        raise RuntimeError('preflight_not_enabled_or_unexpected_configuration')
    if api(mod.API_URL,token=token)!=before:
        raise RuntimeError('task_changed_during_preflight')
    if not live:
        simulated=dict(before)
        simulated['enabled']=False
        calls=[]
        def fake(url,token=None,method='GET',body=None):
            if url==mod.REPORT_URL:
                return {'generated_at_utc':datetime.now(timezone.utc).isoformat(),
                    'agents':{f'ACS-{n:02d}':{'verified':True,'status':'current','health_status':'healthy'}
                    for n in range(1,6)}}
            if url!=mod.API_URL:raise RuntimeError('unexpected_test_url')
            if method=='PATCH':
                if body!={'enabled':True}:raise RuntimeError('unexpected_mutation')
                calls.append(body)
                simulated.update(body)
            return dict(simulated)
        result=mod.guard(True,True,token,fetcher=fake)
        if result['status']!='SCHEDULE_REENABLED_NEXT_RUN_ONLY' or calls!=[{'enabled':True}]:
            raise RuntimeError('simulation_failed')
        return {'passed':True,'scope':'isolated_with_live_readonly_preflight',
            'production_changed':False,'result':result}
    # LIVE TEST: single scheduled-task flag toggled; restore in finally.
    disable_attempted=False
    restored=False
    try:
        disable_attempted=True
        api(mod.API_URL,token=token,method='PATCH',body={'enabled':False})
        disabled=api(mod.API_URL,token=token)
        if mod.validate_task(disabled) or disabled.get('enabled') is not False or not same_config(before,disabled):
            raise RuntimeError('disable_or_configuration_verification_failed')
        result=mod.guard(True,True,token,fetcher=api)
        after=api(mod.API_URL,token=token)
        if result['status']!='SCHEDULE_REENABLED_NEXT_RUN_ONLY' or after.get('enabled') is not True or not same_config(before,after):
            raise RuntimeError('controller_reenable_verification_failed')
        restored=True
        return {'passed':True,'scope':'controlled_production_host_api_test',
            'production_restored':True,'result':result,
            'unattended_github_recovery_proven':False}
    finally:
        if disable_attempted and not restored:
            try:
                api(mod.API_URL,token=token,method='PATCH',body={'enabled':True})
                after=api(mod.API_URL,token=token)
                if after.get('enabled') is not True or not same_config(before,after):
                    raise RuntimeError('rollback_did_not_verify')
                print('ROLLBACK: task enabled and original configuration verified',flush=True)
            except Exception as exc:
                print('CRITICAL: RESTORE NOT VERIFIED — manually enable task 1524414!',flush=True)
                print('Rollback error type:',type(exc).__name__,flush=True)
                raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    token=os.getenv('API_TOKEN') or os.getenv('PYTHONANYWHERE_API_TOKEN')
    if not token:
        print('BLOCKED: missing token; no changes made')
        return 2
    if args.execute and os.getenv('USER')!='rafa1215':
        print('BLOCKED: live test must run on PythonAnywhere as rafa1215')
        return 2
    try:
        result=test(imported_guard(),token,args.execute)
        code=0
    except Exception as exc:
        result={'passed':False,'scope':'controlled_live' if args.execute else 'simulation',
            'error_type':type(exc).__name__,'error':str(exc)[:140]}
        code=2
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),**result},indent=2)+'\n')
    print(json.dumps(result,indent=2))
    print('Evidence:',OUT)
    return code

if __name__=='__main__':
    sys.exit(main())
