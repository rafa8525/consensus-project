from pathlib import Path
from typing import Any, Union
import json
import datetime as _dt

__all__ = ["MemoryManager"]

class MemoryManager:
    def __init__(self, root: Union[str, Path] = "memory") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def store(self, data: Any) -> bool:
        """
        Persist data to a timestamped text file and append a JSONL record.
        Always returns a boolean: True on success, False on failure.
        """
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_path = self.root / f"memory_log_{ts}.txt"
        jsonl_path = self.root / "memory_log.jsonl"
        try:
            # Human-readable snapshot
            with txt_path.open("w", encoding="utf-8") as f:
                if isinstance(data, str):
                    f.write(data)
                else:
                    f.write(json.dumps(data, indent=2, default=str))
            print(f"[MemoryManager] Memory log written to: {txt_path}")

            # Machine-readable append
            record = {"timestamp": ts, "data": data}
            with jsonl_path.open("a", encoding="utf-8") as jf:
                jf.write(json.dumps(record, default=str) + "\n")
            print(f"[MemoryManager] Memory log updated: {data}")

            return True
        except Exception as e:
            print(f"[MemoryManager] store failed: {e}")
            return False
