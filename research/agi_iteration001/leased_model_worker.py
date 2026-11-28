"""Bounded offline inference with leased ownership; research-only, no network or AI API."""
import argparse, json
from pathlib import Path
from leased_worker import claim, complete, connect, model_job, setup
from local_inference import load_checkpoint, predict
from worker_runtime import load_registry

def run_once(db, registry_path, checkpoint_path, agent_id, now=None):
    # All resources are validated before claiming any task.
    registry = load_registry(registry_path)
    if agent_id not in registry:
        raise ValueError("Unknown role")
    checkpoint = load_checkpoint(checkpoint_path)
    path = Path(db)
    if not path.is_file():
        raise ValueError("Queue must already exist")
    c = connect(path)
    try:
        setup(c)
        owned = claim(c, agent_id, seconds=30, now=now)
        if owned is None:
            return None
        result = model_job(owned, checkpoint, predict)
        # Completion will fail closed if ownership expired.
        success = complete(c, owned, result, now=now)
        return {"task_id": owned["task_id"], "completed": success,
                "prediction": result["prediction"] if success else None,
                "mode": "LEASED_OFFLINE_INFERENCE"}
    finally:
        c.close()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--registry", default=str(Path(__file__).with_name("agents_registry.json")))
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--agent", required=True)
    a = p.parse_args()
    print(json.dumps(run_once(a.db, a.registry, a.checkpoint, a.agent)))

if __name__ == "__main__":
    main()
