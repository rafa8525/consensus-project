from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import time, json, uuid, traceback

LOG_DIR = Path("memory/logs/agents")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

@dataclass
class AgentContext:
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_ts: str = field(default_factory=now_ts)
    meta: Dict[str, Any] = field(default_factory=dict)
    out_dir: Path = field(default=LOG_DIR)

class AgentError(Exception):
    pass

class Agent:
    name: str = "agent"

    def __init__(self, ctx: AgentContext):
        self.ctx = ctx

    def log_event(self, kind: str, **data: Any) -> None:
        _jsonl(LOG_DIR / "events.jsonl", {
            "ts": now_ts(),
            "trace": self.ctx.trace_id,
            "agent": self.name,
            "kind": kind,
            **data,
        })

    def write_artifact(self, relpath: str, content: str) -> Path:
        p = self.ctx.out_dir / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.log_event("artifact", path=str(p))
        return p

    def run(self) -> Dict[str, Any]:
        raise NotImplementedError

    def safe_run(self) -> Dict[str, Any]:
        try:
            self.log_event("start")
            out = self.run()
            self.log_event("done", result="ok")
            return out
        except Exception as e:
            self.log_event("error", error=str(e), traceback=traceback.format_exc())
            raise
