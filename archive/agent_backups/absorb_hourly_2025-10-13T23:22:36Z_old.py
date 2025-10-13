cd ~/consensus-project
cat > tools/absorb_hourly.py <<'PY'
#!/usr/bin/env python3
import os, sys, json, subprocess, errno, fcntl, time
from pathlib import Path
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
LOG = Path("memory/logs/absorb/absorb_success_log.jsonl")
LOCK_DIR = Path("memory/logs/absorb")

AM_START = dtime(9, 30)    # 09:30
AM_END   = dtime(10, 29)   # 10:29
PM_START = dtime(15, 30)   # 15:30
PM_END   = dtime(16, 29)   # 16:29

PA_TIMEOUT = 1800  # 30m, under PA limit
PA_MAX_RETRIES = 1

def load_log():
    entries = []
    if LOG.exists():
        for line in LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line: continue
            try: entries.append(json.loads(line))
            except Exception: pass
    return entries

def day_has(entries, day_date, window):
    for e in entries:
        if e.get("window") != window: continue
        ts = e.get("ts")
        try: dt = datetime.fromisoformat(ts)
        except Exception: continue
        dt_local = dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)
        if dt_local.date() == day_date: return True
    return False

def between(now_t, start_t, end_t):
    return (now_t >= start_t) and (now_t <= end_t)

def is_dst_transition_day(dt):
    try:
        test_times = [
            dt.replace(hour=0,  minute=30),
            dt.replace(hour=1,  minute=30),
            dt.replace(hour=2,  minute=30),
            dt.replace(hour=3,  minute=30),
            dt.replace(hour=12, minute=0),
            dt.replace(hour=23, minute=30),
        ]
        offsets = set()
        for t in test_times:
            try:
                offsets.add(t.replace(tzinfo=TZ).utcoffset())
            except Exception:
                continue
        return len(offsets) > 1
    except Exception:
        return False

def detect_pythonanywhere():
    if os.path.exists('/etc/pythonanywhere'):
        return True
    env = os.environ
    hints = [
        env.get('PA_DOMAIN',''),
        env.get('PYTHONANYWHERE_DOMAIN',''),
        env.get('HOSTNAME',''),
        os.path.dirname(os.path.expanduser('~')),
        env.get('PATH',''),
    ]
    return any('pythonanywhere' in (s or '').lower() for s in hints)

def acquire_lock_safely(lock_path: Path, current_pid: int):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o644)
            os.write(fd, f"{current_pid}\n".encode()); os.fsync(fd)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except OSError as e:
            if e.errno == errno.EEXIST and lock_path.exists():
                try:
                    pid_str = lock_path.read_text().strip()
                    if pid_str.isdigit():
                        pid = int(pid_str)
                        try:
                            os.kill(pid, 0)  # alive
                            print(f"[absorb_hourly] active lock held by PID {pid}; skipping")
                            return None
                        except ProcessLookupError:
                            print(f"[absorb_hourly] removing stale lock (PID {pid})")
                            try:
                                lock_path.unlink(missing_ok=True)
                                time.sleep(0.1 * (attempt + 1))
                                continue
                            except FileNotFoundError:
                                continue
                    else:
                        print(f"[absorb_hourly] invalid PID in lock file; removing and skipping")
                        lock_path.unlink(missing_ok=True)
                        return None
                except Exception as read_error:
                    print(f"[absorb_hourly] error reading lock: {read_error}; skipping")
                    return None
            elif e.errno in (errno.EAGAIN, errno.EACCES):
                print(f"[absorb_hourly] lock busy; skipping")
                return None
            else:
                raise
    print(f"[absorb_hourly] failed to acquire lock after {max_attempts} attempts")
    return None

def run_absorb(window, mode):
    env = os.environ.copy()
    env["RUN_MODE"] = mode
    env["TARGET_WINDOW"] = window

    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCK_DIR / f".lock_{window}"
    me = os.getpid()

    fd = acquire_lock_safely(lock_path, me)
    if fd is None:
        return True  # treat as no-op

    try:
        timeout = PA_TIMEOUT if detect_pythonanywhere() else 3600
        try:
            res = subprocess.run(
                ["/usr/bin/python3", "tools/absorb_runner.py"],
                env=env, timeout=timeout, capture_output=True, text=True
            )
            rc = res.returncode
        except subprocess.TimeoutExpired:
            print(f"[absorb_hourly] {window} {mode} run timed out after {timeout}s")
            return False

        if rc != 0:
            print(f"[absorb_hourly] {window} {mode} run failed (rc={rc})")
            if res.stderr: print(f"[absorb_hourly] stderr: {res.stderr[:200]}")
            return False

        try:
            res2 = subprocess.run(
                ["/usr/bin/python3", "tools/absorb_log_append.py", window],
                timeout=30, capture_output=True, text=True
            )
            if res2.returncode != 0:
                print(f"[absorb_hourly] WARNING: runner ok but logging failed (rc={res2.returncode})")
                if res2.stderr: print(f"[absorb_hourly] logging stderr: {res2.stderr[:200]}")
            else:
                print(f"[absorb_hourly] logged {window} success")
        except subprocess.TimeoutExpired:
            print(f"[absorb_hourly] WARNING: logging timed out for {window}")
        return True
    finally:
        try: fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception: pass
        try: os.close(fd)
        except Exception: pass
        try:
            if lock_path.exists() and lock_path.read_text().strip() == str(me):
                lock_path.unlink()
        except Exception: pass

def run_absorb_with_retry(window, mode, max_retries=None):
    if max_retries is None:
        max_retries = PA_MAX_RETRIES if detect_pythonanywhere() else 2
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            if run_absorb(window, mode):
                return True
        except Exception as e:
            last_err = e
            print(f"[absorb_hourly] {window} attempt {attempt+1} exception: {e}")
        if attempt < max_retries:
            wait_s = min((attempt + 1) * 10, 30)
            print(f"[absorb_hourly] {window} retrying in {wait_s}s (attempt {attempt+2}/{max_retries+1})")
            time.sleep(wait_s)
    msg = f"{window} failed after {max_retries+1} attempts"
    if last_err: msg += f", last error: {last_err}"
    print(f"[absorb_hourly] {msg}")
    return False

def main():
    now = datetime.now(TZ)
    entries = load_log()
    today = now.date()
    am_done = day_has(entries, today, "am")
    pm_done = day_has(entries, today, "pm")
    now_t = now.time()

    if is_dst_transition_day(now):
        print("[absorb_hourly] DST transition day - windows may be looser")

    if not am_done and between(now_t, AM_START, AM_END):
        ok = run_absorb_with_retry("am", "scheduled"); sys.exit(0 if ok else 1)
    if not pm_done and between(now_t, PM_START, PM_END):
        ok = run_absorb_with_retry("pm", "scheduled"); sys.exit(0 if ok else 1)

    if not pm_done and now_t > PM_END:
        ok = run_absorb_with_retry("pm", "catchup"); sys.exit(0 if ok else 1)
    if not am_done and now_t > AM_END:
        ok = run_absorb_with_retry("am", "catchup"); sys.exit(0 if ok else 1)

    print("[absorb_hourly] nothing due right now"); sys.exit(0)

if __name__ == "__main__":
    main()
PY
chmod +x tools/absorb_hourly.py
python3 -m py_compile tools/absorb_hourly.py && echo "hourly.py: syntax ok"
