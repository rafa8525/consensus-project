from typing import Optional, Dict, Any

class Agent:
    def __init__(self, ctx: Optional[Dict[str, Any]] = None) -> None:
        if ctx is None:
            ctx = {}
        self.ctx: Dict[str, Any] = ctx
