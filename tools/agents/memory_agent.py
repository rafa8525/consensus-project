from pathlib import Path
from datetime import datetime, timezone
from .utils import log

def main(note="ok"):
    outdir = Path("memory/from_agents")
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / f"note_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.txt"
    p.write_text(note + "\n", encoding="utf-8")
    log(f"[memory_agent] wrote {p}")
    return 0

if __name__ == "__main__":
    import sys
    note = " ".join(sys.argv[1:]) or "ok"
    raise SystemExit(main(note))
