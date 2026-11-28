"""Sandbox-only role dispatcher. Does not execute AI agents or external commands."""
import hashlib
import json
from pathlib import Path

OPERATIONS = {
    'review_hypothesis': ['Define falsifiable claim', 'Identify confounds', 'Request independent review'],
    'design_experiment': ['Set baseline', 'Define held-out data', 'Set budgets and stop conditions'],
    'evaluate_evidence': ['Check data separation', 'Check reproducibility', 'Report limitations'],
}

class InvalidTask(ValueError):
    pass

def load_registry(path):
    data = json.loads(Path(path).read_text())
    agents = data['agents']
    if len(agents) != 55 or len({a['id'] for a in agents}) != 55:
        raise InvalidTask('Expected 55 unique agent definitions')
    if any(a['status'] != 'PROPOSED_UNVERIFIED' or a['production_enabled'] for a in agents):
        raise InvalidTask('Only disabled, unverified definitions permitted')
    return {a['id']:a for a in agents}

def simulate(tasks, registry):
    if not isinstance(tasks, list) or len(tasks) > 55:
        raise InvalidTask('Batch must contain 0-55 tasks')
    out = []
    for task in tasks:
        if not isinstance(task, dict) or task.get('agent_id') not in registry:
            raise InvalidTask('Unknown agent')
        op, objective = task.get('operation'), task.get('objective')
        if op not in OPERATIONS or not isinstance(objective, str) or not 0 < len(objective.strip()) <= 500:
            raise InvalidTask('Invalid operation or objective')
        agent = registry[task['agent_id']]
        record = {'agent_id':agent['id'], 'name':agent['name'], 'division':agent['agi_division'],
                  'operation':op, 'objective':objective.strip(), 'suggested_steps':OPERATIONS[op],
                  'mode':'STATIC_ROLE_SIMULATION', 'agent_executed':False, 'model_trained':False,
                  'production_changed':False, 'independently_verified':False}
        record['sha256'] = hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
        out.append(record)
    return {'schema_version':1, 'task_count':len(out), 'results':out}

def save_new(path, result):
    path = Path(path)
    if not path.parent.is_dir():
        raise InvalidTask('Output directory must exist')
    payload = (json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if len(payload)>1000000:
        raise InvalidTask('Record too large')
    with path.open('xb') as f:
        f.write(payload)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default=str(Path(__file__).with_name('agents_registry.json')))
    ap.add_argument('--tasks', required=True)
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    task_path=Path(args.tasks)
    if task_path.stat().st_size>1000000:
        raise InvalidTask('Task input too large')
    save_new(args.out,simulate(json.loads(task_path.read_text()),load_registry(args.registry)))
    print('Simulation complete; no agent executed')
