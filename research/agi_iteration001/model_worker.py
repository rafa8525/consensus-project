"""Offline learned-model inference in an existing isolated SQLite task queue."""
import argparse,hashlib,json
from pathlib import Path
from local_inference import load_checkpoint,predict
from worker_runtime import connect,setup,load_registry,claim,now

def run_model_once(con,registry,model,agent_id,worker_id):
    if agent_id not in registry or not isinstance(worker_id,str) or not 0<len(worker_id)<=80:
        raise ValueError('Invalid worker')
    task=claim(con,agent_id,worker_id)
    if task is None: return None
    tid,operation,objective,deps_json=task
    try:
        receipts=[]
        for dep in json.loads(deps_json):
            row=con.execute('SELECT result_json FROM tasks WHERE id=? AND status=?',(dep,'done')).fetchone()
            if row is None: raise ValueError('Missing completed dependency')
            receipts.append({'task_id':dep,'digest':json.loads(row[0])['digest']})
        inference=predict(model['model'],objective)
        result={'task_id':tid,'agent_id':agent_id,'agent_name':registry[agent_id]['name'],
                'operation':operation,'objective':objective,'dependency_receipts':receipts,
                'inference':inference,'inference_matches_assigned_operation':inference['label']==operation,
                'checkpoint_sha256':model['sha256'],'mode':'OFFLINE_TRAINED_NAIVE_BAYES',
                'is_ai_inference':True,'is_llm':False,'model_trained_in_this_task':False,
                'production_changed':False}
        result['digest']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
        con.execute('BEGIN IMMEDIATE')
        try:
            changed=con.execute('UPDATE tasks SET status=?,finished_at=?,result_json=? WHERE id=? AND status=? AND worker=?',
                                ('done',now(),json.dumps(result,sort_keys=True),tid,'running',worker_id)).rowcount
            if changed!=1: raise RuntimeError('Task ownership changed')
            con.execute('INSERT INTO messages(task_id,sender,receiver,payload,created_at) VALUES(?,?,?,?,?)',
                        (tid,agent_id,'research_collective',json.dumps({'event':'model_inference_completed',
                         'digest':result['digest'],'label':inference['label']}),now()))
            con.execute('COMMIT')
        except BaseException:
            con.execute('ROLLBACK')
            raise
        return result
    except Exception as exc:
        con.execute('UPDATE tasks SET status=?,finished_at=?,result_json=? WHERE id=? AND status=? AND worker=?',
                    ('failed',now(),json.dumps({'error':type(exc).__name__}),tid,'running',worker_id))
        raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db',required=True)
    p.add_argument('--registry',default=str(Path(__file__).with_name('agents_registry.json')))
    p.add_argument('--checkpoint',required=True)
    p.add_argument('--agent',required=True)
    p.add_argument('--worker-id',required=True)
    args=p.parse_args()
    if not Path(args.db).exists(): raise ValueError('DB must already exist')
    model=load_checkpoint(args.checkpoint)
    registry=load_registry(args.registry)
    con=connect(args.db)
    setup(con)
    try: print(json.dumps(run_model_once(con,registry,model,args.agent,args.worker_id)))
    finally: con.close()
if __name__=='__main__': main()
