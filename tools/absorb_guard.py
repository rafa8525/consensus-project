#!/usr/bin/env python3
# Auto-triggers /memory/absorb when memory/ has newer commits than server metrics.
import json, subprocess, urllib.request, urllib.error, os
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.home() / "consensus-project"
METRICS_URL = "https://rafa1215.pythonanywhere.com/metrics"
ABSORB_URL  = "https://rafa1215.pythonanywhere.com/memory/absorb"
LOG_DIR = ROOT / "memory" / "logs" / "agents" / "heartbeat"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOG_DIR / f"absorb_guard_{datetime.now(timezone.utc).date().isoformat()}.log"

def iso_to_dt(s: str):
    if not s: return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def log(msg: str):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
def last_memory_commit_dt():
    try:
        out = subprocess.check_output(
            ["git","log","-1","--pretty=%cI","--","memory"],
            cwd=ROOT, text=True
        ).strip()
        return iso_to_dt(out)
    except Exception as e:
        log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] absorb_guard: git error: {e}")
        return None
def fetch_metrics():
    try:
        with urllib.request.urlopen(METRICS_URL, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] absorb_guard: metrics fetch error: {e}")
        return {}

def post_absorb():
    try:
        tok = json.loads((Path.home()/".pa_env.json").read_text()).get("VOICE_TOKEN","")
        if not tok:
            raise RuntimeError("VOICE_TOKEN missing in ~/.pa_env.json")
        req = urllib.request.Request(ABSORB_URL, method="POST", headers={"X-Voice-Token": tok})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] absorb_guard: absorb POST error: {e}")
        return {"ok": False}
def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    m = fetch_metrics()
    last_absorb = iso_to_dt(m.get("last_memory_absorb_iso"))
    last_commit = last_memory_commit_dt()

    if last_commit and (not last_absorb or last_absorb < last_commit):
        resp = post_absorb()
        log(f"[{now}] absorb_guard: TRIGGERED; commit newer than absorb. resp.ok={resp.get('ok')} commit={resp.get('commit')}")
    else:
        log(f"[{now}] absorb_guard: OK; absorb up-to-date.")
if __name__ == "__main__":
    main()
