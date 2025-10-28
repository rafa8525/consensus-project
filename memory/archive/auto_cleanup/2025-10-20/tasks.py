from mcl_v2.paths import BASE
from mcl_v2.utils import now_iso
import subprocess

def task_auto_git_sync() -> None:
    """Optional external task; if present, call bounded; else write stub log."""
    script = BASE / "auto_git_sync.py"
    (BASE / "memory/logs/scheduler").mkdir(parents=True, exist_ok=True)
    logf = BASE / "memory/logs/scheduler/auto_git_sync.log"
    if not script.exists():
        with logf.open("a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] (stub) no auto_git_sync.py present\n")
        return
    try:
        res = subprocess.run(
            ["python3.10", str(script)],
            capture_output=True, text=True, timeout=10
        )
        with logf.open("a", encoding="utf-8") as f:
            out = (res.stdout or "").strip().replace("\n", " ")[:200]
            f.write(f"[{now_iso()}] rc={res.returncode} out={out}\n")
    except subprocess.TimeoutExpired:
        with logf.open("a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] TIMEOUT\n")
