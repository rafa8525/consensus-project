from __future__ import annotations
from pathlib import Path
import time, json

LOG = Path("memory/logs/agents/metrics.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

def record(metric: str, **labels):
    item = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "metric": metric, **labels}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item) + "\n")
