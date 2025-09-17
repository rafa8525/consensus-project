import os
import signal
import sys
from mcl_v2.paths import LOCK

def acquire_or_exit() -> None:
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip() or "0")
        except Exception:
            pid = 0
        if pid > 0:
            try:
                os.kill(pid, 0)
                print(f"mcl_v2 already running (pid={pid})")
                sys.exit(0)
            except Exception:
                pass
    LOCK.write_text(str(os.getpid()), encoding="utf-8")

    def _cleanup(*_):
        try:
            if LOCK.exists():
                LOCK.unlink()
        finally:
            os._exit(0)

    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)
