from datetime import datetime
import random
from mcl_v2.paths import HB_FILE

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def write_heartbeat() -> None:
    HB_FILE.write_text(now_iso() + "\n", encoding="utf-8")

def jitter(base_seconds: float, spread: float = 0.25) -> float:
    j = base_seconds * spread
    return max(0.0, base_seconds + random.uniform(-j, j))
