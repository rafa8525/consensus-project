from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import traceback


class Agent:
    """Base class for runtime agents.

    safe_run() is the durable execution boundary used by Supervisor.  It
    records failures as structured results instead of allowing one child agent
    to prevent the Supervisor from writing its own execution evidence.
    """

    def __init__(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        self.ctx: Dict[str, Any] = {} if ctx is None else ctx

    def run(self) -> Dict[str, Any]:
        raise NotImplementedError

    def safe_run(self) -> Dict[str, Any]:
        try:
            result = self.run()
            return {"ok": True, "result": result}
        except Exception as exc:
            return {
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
                "traceback": traceback.format_exc(limit=8)[-4000:],
            }

    def write_artifact(self, filename: str, content: str) -> Path:
        root = Path("memory/logs/agents")
        root.mkdir(parents=True, exist_ok=True)
        target = root / filename
        target.write_text(content, encoding="utf-8")
        return target
