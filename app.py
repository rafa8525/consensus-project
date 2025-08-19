# app.py
import os, sys, hmac, hashlib, json, subprocess
from pathlib import Path
from datetime import datetime, timezone, date
from flask import Flask, request, jsonify

# --- Safety defaults (SMS off by default) ---
os.environ.setdefault("TWILIO_SILENCE", "1")
os.environ.setdefault("TWILIO_ALLOW_SEND", "0")

# --- Project root ---
CP_ROOT = Path("/home/rafa1215/consensus-project").resolve()

# --- Tokens (set via ~/.pa_env.json or PA Web->Env) ---
VOICE_TOKEN = os.getenv("VOICE_TOKEN", "")
GEO_TOKEN   = os.getenv("GEO_TOKEN",  "bvJkujAO1MOtHL6WL5RhbdayMEF7ILBnIy4OFzXzkgg")
GH_SECRET   = os.getenv("GITHUB_WEBHOOK_SECRET", "")  # set this below in step 3

# --- Logs ---
LOGS = CP_ROOT / "memory" / "logs"
LOGS.mkdir(parents=True, exist_ok=True)
GEOF_DIR = LOGS / "geofencing"; GEOF_DIR.mkdir(exist_ok=True)
REM_DIR  = LOGS / "reminders";  REM_DIR.mkdir(exist_ok=True)
HB_DIR   = LOGS / "heartbeat";  HB_DIR.mkdir(exist_ok=True)
SYS_DIR  = LOGS / "system";     SYS_DIR.mkdir(exist_ok=True)

HTTP_INGEST = GEOF_DIR / f"http_ingest_{date.today().isoformat()}.log"
VOICE_TRIG  = REM_DIR  / f"voice_trigger_{date.today().isoformat()}.log"
ABSORB_HB   = HB_DIR   / "memory_absorption_heartbeat.log"   # rolling (git-ignored)
ABSORB_LAST = HB_DIR   / "last_absorbed_commit.txt"          # last commit absorbed

app = Flask("consensus_app")

def _nowiso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _run(cmd):
    r = subprocess.run(cmd, cwd=str(CP_ROOT), text=True, capture_output=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()

def _append(p: Path, line: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f: f.write(line + "\n")

def _count_today(path: Path, needle: str = "") -> int:
    if not path.exists(): return 0
    d = date.today().isoformat()
    n = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for ln in f:
            if d in ln and (needle in ln if needle else True):
                n += 1
    return n

def absorb_memory(source="manual"):
    """
    Pulls latest repo, records last absorbed commit, and appends a heartbeat.
    ChatGPT Voice should read ABSORB_LAST / ABSORB_HB to know freshness.
    """
    ts = _nowiso()
    _run(["git", "fetch", "origin"])
    # Stay on current branch but fast-forward
    _run(["git", "pull", "--ff-only", "origin", "v1.1-dev"])
    rc, head, _ = _run(["git", "rev-parse", "HEAD"])
    commit_txt = head if rc == 0 else "unknown"
    ABSORB_LAST.write_text(f"{commit_txt} {ts}\n", encoding="utf-8")
    _append(ABSORB_HB, f"[{ts}] source={source} commit={commit_txt}")
    return {"ok": True, "ts": ts, "commit": commit_txt, "source": source}

# ------------------- Existing endpoints kept -------------------

@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok"

@app.route("/metrics", methods=["GET"])
def metrics():
    # basic version
    rc, ver, _ = _run(["git", "log", "-1", "--pretty=%H %cI %s"])
    resp = {
        "ok": True,
        "ts": _nowiso(),
        "version": ver if rc == 0 else "",
        # voice / geo as before (may be zero if unused)
        "voice_trigger_hits_today": _count_today(REM_DIR / f"voice_trigger_{date.today().isoformat()}.log"),
        "geo_ingests_today": _count_today(HTTP_INGEST),
        "twilio_allow_send": os.getenv("TWILIO_ALLOW_SEND", "0") == "1",
        # NEW: memory absorption metrics
        "memory_absorb_hits_today": _count_today(ABSORB_HB),
        "last_memory_absorb_iso": (ABSORB_LAST.read_text().split()[-1] if ABSORB_LAST.exists() else None),
    }
    return jsonify(resp)

@app.route("/geo", methods=["GET"])
@app.route("/geo/", methods=["GET"])
def geo():
    token = request.args.get("token", "")
    if not token or token != GEO_TOKEN:
        return jsonify({"ok": False, "rc": 401, "err": "unauthorized"}), 401
    try:
        lat = float(request.args["lat"]); lon = float(request.args["lon"])
        acc = int(round(float(request.args.get("acc", "50"))))
    except Exception:
        return jsonify({"ok": False, "rc": 400, "err": "bad-params"}), 400
    src = request.args.get("src", "http")
    rc, out, err = _run(["python3","tools/geofence_engine.py","--lat",str(lat),"--lon",str(lon),"--acc",str(acc),"--source",src])
    _append(HTTP_INGEST, f"[{_nowiso()}] lat={lat} lon={lon} acc={acc} src={src} rc={rc} out={out} err={err}")
    return jsonify({"ok": rc==0, "rc": rc, "out": out, "err": err, "ts": _nowiso(), "acc_used": acc})

@app.route("/voice_trigger", methods=["POST"])
def voice_trigger():
    tok = request.headers.get("X-Voice-Token","")
    if not tok or tok != VOICE_TOKEN:
        return jsonify({"ok": False, "rc": 401, "err": "unauthorized"}), 401
    _append(REM_DIR / f"voice_trigger_{date.today().isoformat()}.log",
            json.dumps({"ts": _nowiso(), "ip": request.remote_addr, "ua": request.headers.get("User-Agent",""), "keys": list(request.form.keys())}))
    # This endpoint stays a dry-run notifier; real SMS is guarded elsewhere
    return jsonify({"ok": True, "send": {"status":"skipped"}, "ts": _nowiso()})

# ------------------- NEW: Manual absorb endpoint -------------------

@app.route("/memory/absorb", methods=["POST"])
def memory_absorb_manual():
    tok = request.headers.get("X-Voice-Token","")
    if not tok or tok != VOICE_TOKEN:
        return jsonify({"ok": False, "rc": 401, "err": "unauthorized"}), 401
    return jsonify(absorb_memory(source="manual"))

# ------------------- NEW: GitHub webhook (push) -------------------

def _verify_github_signature(raw_body: bytes) -> bool:
    if not GH_SECRET: 
        return False
    sig = request.headers.get("X-Hub-Signature-256","")
    if not sig.startswith("sha256="): 
        return False
    digest = "sha256=" + hmac.new(GH_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    # Use constant-time compare
    return hmac.compare_digest(sig, digest)

@app.route("/github_webhook", methods=["POST"])
def github_webhook():
    raw = request.get_data()
    if not _verify_github_signature(raw):
        return jsonify({"ok": False, "rc": 401, "err": "bad-signature"}), 401
    event = request.headers.get("X-GitHub-Event","")
    if event != "push":
        return jsonify({"ok": True, "skipped": f"event={event}"}), 200
    payload = request.get_json(silent=True) or {}
    ref = payload.get("ref","")
    # Only absorb on v1.1-dev pushes (adjust if you want more branches)
    if ref not in ("refs/heads/v1.1-dev",):
        return jsonify({"ok": True, "skipped": f"ref={ref}"}), 200
    result = absorb_memory(source="github_push")
    return jsonify(result), 200

# WSGI entrypoint
application = app
# --- VOICE LAST ABSORB (reads /metrics) ---
from flask import request, jsonify  # likely already imported; safe to re-import
import urllib.request, json, pathlib

def _voice_token():
    try:
        p = pathlib.Path("/home/rafa1215/.pa_env.json")
        return json.loads(p.read_text()).get("VOICE_TOKEN","")
    except Exception:
        return ""

@app.get("/voice/last_absorb")
def voice_last_absorb():
    # Optional auth: require X-Voice-Token if present in ~/.pa_env.json
    tok = _voice_token()
    if tok and request.headers.get("X-Voice-Token","") != tok:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    # Call our own /metrics to avoid duplicating logic
    base = request.url_root.rstrip("/")
    try:
        with urllib.request.urlopen(base + "/metrics", timeout=10) as r:
            m = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return jsonify({"ok": False, "text": "I can't reach metrics right now.", "error": str(e)}), 503

    ts   = m.get("last_memory_absorb_iso")
    hits = int(m.get("memory_absorb_hits_today", 0) or 0)

    if not ts:
        text = "No GitHub memory absorb is recorded yet."
    else:
        text = f"The latest GitHub memory absorb was at {ts} UTC. Absorbs today: {hits}."

    return jsonify({"ok": True, "text": text, "ts": ts, "hits_today": hits})
# --- END VOICE LAST ABSORB ---

# --- VOICE BARCODE HELPERS (BEGIN) ---
from pathlib import Path as _VPath
from datetime import datetime as _VDT, timezone as _VTZ
from flask import request as _VREQ, jsonify as _VJ
import json as _VJSON, re as _VRE, subprocess as _VSUB

_CACHE = _VPath.home() / "consensus-project" / "memory" / "logs" / "nutrition" / "barcode_cache.json"
def _voice_guard():
    try:
        cfg = _VJSON.loads((_VPath.home()/".pa_env.json").read_text())
        stored = cfg.get("VOICE_TOKEN","")
        sent   = _VREQ.headers.get("X-Voice-Token","")
        return bool(stored) and stored == sent
    except Exception:
        return False
def _try_refresh_cache():
    if not _CACHE.exists():
        try:
            _VSUB.check_call(["python3","tools/barcode_cache.py"],
                             cwd=str(_VPath.home()/ "consensus-project"))
        except Exception:
            pass

def _load_cache():
    _try_refresh_cache()
    if not _CACHE.exists():
        return []
    try:
        return _VJSON.loads(_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return []
def _summarize(records):
    try:
        records = records or []
        n = len(records)
        keto = sum(1 for r in records if (r.get("class","").lower().startswith("keto")))
        slightly = sum(1 for r in records if (r.get("class","").lower().startswith("slightly")))
        import re as __re
        nonfood = sum(1 for r in records if __re.search(r"(tissue|towel|sanitizer|soap|detergent|shampoo|deodorant|lotion|trash bag)", (r.get("item") or "").lower()))
        seen, last_items = set(), []
        for r in reversed(records):
            it = (r.get("item") or "(unknown)").strip()
            if it and it not in seen:
                last_items.append(it); seen.add(it)
            if len(last_items) == 10: break
        parts = [f"I have {n} cached barcode rows. Keto-tagged: {keto}, Slightly Keto: {slightly}, non-food: {nonfood}."]
        if last_items:
            parts.append("Recent items: " + ", ".join(last_items[:5]) + ("" if len(last_items)<=5 else ", ..."))
        return " ".join(parts)
    except Exception:
        return "I have a cached barcode snapshot, but summarizing it failed."
