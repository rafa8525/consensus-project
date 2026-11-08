#!/usr/bin/env python3
"""Read-only ACS-01 schedule comparison against saved pre-interruption backup.

Does not print command, token, description, or arbitrary API values.
Does not PATCH or change the task. Intended after controlled-test rollback.
"""
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

BACKUP=Path.home()/'.local/state/ai-consensus/phase1_original_acs01_schedule.json'
GUARD=Path('/tmp/acs_guard.py')
STABLE=('id','command','interval','hour','minute','description')
EXCLUDED=('enabled',)

def compare(before,after):
    if not isinstance(before,dict) or not isinstance(after,dict):
        return {'status':'BLOCKED_invalid_records'}
    fields=sorted(set(before)|set(after))
    modified=[k for k in fields if k not in EXCLUDED and before.get(k)!=after.get(k)]
    key_changes=[k for k in fields if (k in before)!=(k in after)]
    return {'status':'MATCH' if not modified and not key_changes else 'METADATA_DIFF',
            'modified_field_names':modified,
            'key_presence_changes':key_changes,
            'stable_fields_match':all(k in before and k in after and before[k]==after[k] for k in STABLE),
            'baseline_enabled':before.get('enabled') is True,
            'current_enabled':after.get('enabled') is True,
            'no_changes_made':True}

def main():
    if not GUARD.is_file() or not BACKUP.is_file():
        print(json.dumps({'status':'BLOCKED_missing_guard_or_backup','no_changes_made':True}))
        return 2
    token=os.getenv('API_TOKEN') or os.getenv('PYTHONANYWHERE_API_TOKEN')
    if not token:
        print(json.dumps({'status':'BLOCKED_no_token','no_changes_made':True}))
        return 2
    spec=importlib.util.spec_from_file_location('read_only_guard',GUARD)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    try:
        original=json.loads(BACKUP.read_text())['task']
        current=mod.fetch_json(mod.API_URL,token=token)
        if mod.validate_task(current) or mod.validate_task(original):
            raise RuntimeError('unexpected_task_id_or_command')
        result=compare(original,current)
        result['current_guard_status']=mod.decide(mod.inspect_report(mod.fetch_json(mod.REPORT_URL),datetime.now(timezone.utc)),current)
    except Exception as exc:
        result={'status':'BLOCKED_read_failed','error_type':type(exc).__name__,'no_changes_made':True}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if result.get('status') in ('MATCH','METADATA_DIFF') and result.get('current_enabled') else 2

if __name__=='__main__':
    raise SystemExit(main())
