cat > tools/absorb_log_append.py <<'PY'
#!/usr/bin/env python3
"""
Append a successful absorb event to the JSONL history and update state.

Usage:
  python3 tools/absorb_log_append.py [am|pm]
  or: TARGET_WINDOW=am|pm python3 tools/absorb_log_append.py
  Optional: ABSORB_TS_ISO=<iso8601> to override timestamp
"""
import os, sys, json, tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
LOG_PATH = Path("memory/logs/absorb/absorb_success_log.jsonl")
STATE_PATH = Path("memory/logs/absorb/absorb_state.json")

def ensure_dirs():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def choose_window(argv) -> str:
    if len(argv) >= 2 and argv[1] in ("am","pm"):
        return argv[1]
    env = os.environ.get("TARGET_WINDOW","").lower()
    if env in ("am","pm"): return env
    return "pm"

def choose_timestamp() -> str:
    ts_env = os.environ.get("ABSORB_TS_ISO","").strip()
    if ts_env:
        try:
            datetime.fromisoformat(ts_env)
            return ts_env
        except Exception:
            pass
    return datetime.now(TZ).isoformat()

def append_history(ts_iso: str, window: str) -> None:
    entry = {"ts": ts_iso, "window": window}
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def atomic_state_update(state_path: Path, state_data: dict) -> None:
    tmp_dir = state_path.parent
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=tmp_dir, suffix=".tmp", encoding="utf-8", delete=False) as tmp:
        try:
            json.dump(state_data, tmp, ensure_ascii=False, indent=2)
            tmp.flush(); os.fsync(tmp.fileno())
            os.rename(tmp.name, str(state_path))  # atomic on same FS
        except Exception as e:
            try: os.unlink(tmp.name)
            except Exception: pass
            raise RuntimeError(f"Failed to update state file: {e}")

def update_state(ts_iso: str, window: str) -> None:
    state = {}
    if STATE_PATH.exists():
        try:
            content = STATE_PATH.read_text(encoding="utf-8").strip()
            if content:
                state = json.loads(content)
                if not isinstance(state, dict):
                    print("[absorb_log_append] WARNING: state file contains non-dict, resetting")
                    state = {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"[absorb_log_append] WARNING: corrupt state file ({e}), resetting")
            state = {}
        except Exception as e:
            print(f"[absorb_log_append] WARNING: error reading state file ({e}), resetting")
            state = {}

    state["last_attempt"] = ts_iso
    if window == "am": state["last_am_success"] = ts_iso
    else:              state["last_pm_success"] = ts_iso
    state["last_error"] = ""

    atomic_state_update(STATE_PATH, state)

def main(argv):
    ensure_dirs()
    window = choose_window(argv)
    ts_iso = choose_timestamp()
    append_history(ts_iso, window)
    update_state(ts_iso, window)
    print(f"Appended {window} success @ {ts_iso}")

if __name__ == "__main__":
    main(sys.argv)
PY
chmod +x tools/absorb_log_append.py
python3 -m py_compile tools/absorb_log_append.py && echo "log_append.py: syntax ok"
