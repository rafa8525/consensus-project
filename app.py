# app.py — single-file bridge for ChatGPT Voice ↔ backend (PythonAnywhere-ready)
# Endpoints:
#   GET  /                     -> ping/version summary
#   GET  /health, /healthz     -> quick system sanity
#   GET  /version              -> git head
#   POST /voice_trigger        -> baseline 200; optional SMS via twilio_guard; token-protected
#   GET  /geo                  -> ingest a location ping (uses GEO_TOKEN; int accuracy to engine)
#   GET  /voice/status         -> last absorption + last GitHub memory update
#   GET  /ask                  -> simple memory Q&A over search_index.json
#   GET  /remind               -> schedule a reminder (text, when)

import os, json, subprocess
from pathlib import Path
from flask import Flask, request, jsonify
from datetime import datetime, timezone

# ---- Paths
BASE = Path.home() / "consensus-project"
MEM  = BASE / "memory"
LOGD = MEM / "logs"
GEOD = LOGD / "geofencing"
REMD = LOGD / "reminders"

# ---- Flask
app = Flask(__name__)
app.url_map.strict_slashes = False  # accept both /route and /route/

# ---- Config / Env
GEO_TOKEN   = os.environ.get("GEO_TOKEN", "bvJkujAO1MOtHL6WL5RhbdayMEF7ILBnIy4OFzXzkgg")
VOICE_TOKEN = os.environ.get("VOICE_TOKEN")  # if set, /voice_trigger requires X-Voice-Token header
TWILIO_TO   = os.environ.get("TWILIO_TO")     # e.g. +1XXXXXXXXXX
TWILIO_FROM = os.environ.get("TWILIO_FROM")   # e.g. +1XXXXXXXXXX
ALLOW_SEND  = os.environ.get("TWILIO_ALLOW_SEND", "0") == "1"

# Safe SMS wrapper (guarded; pre-commit-safe)
try:
    from common.twilio_guard import send_sms
except Exception:
    send_sms = None  # baseline works without SMS

# ---- Helpers
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def run(cmd):
    p = subprocess.Popen(cmd, cwd=str(BASE),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=60)
    return p.returncode, out.strip(), err.strip()

def dated_log_path(dirpath: Path, base_name: str) -> Path:
    dirpath.mkdir(parents=True, exist_ok=True)
    return dirpath / f"{base_name}_{datetime.now().date()}.log"

def append_log(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")

def git_head():
    rc, out, err = run(["git", "log", "-1", "--format=%H %cI %s"])
    return out if rc == 0 else None

# -----------------------------
# Root & health
# -----------------------------
@app.get("/")
def root():
    return jsonify(ok=True, ts=now_iso(), version=git_head())

@app.get("/health")
def health():
    status = {"time": now_iso(), "version": git_head()}
    idx = MEM/"index"/"search_index.json"
    status["index_ok"] = idx.exists()
    if idx.exists():
        try:
            j = json.loads(idx.read_text(encoding="utf-8"))
            status["indexed_files"] = j.get("total_files")
            status["index_generated_at"] = j.get("generated_at")
        except Exception:
            status["indexed_files"] = None

    hb = LOGD/"heartbeat"/"memory_absorption_heartbeat.log"
    if hb.exists():
        try:
            last = hb.read_text(encoding="utf-8").strip().splitlines()[-1]
            if last.startswith("[") and "]" in last:
                status["last_absorption_iso"] = last.split("]")[0][1:]
        except Exception:
            pass

    today = datetime.utcnow().strftime("%Y-%m-%d")
    status["geofence_heartbeat_today"] = (GEOD/f"heartbeat_{today}.md").exists()

    return jsonify(ok=True, **status)

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/version")
def version():
    return jsonify(ok=True, version=git_head(), ts=now_iso())

# -----------------------------
# /voice_trigger (POST, token-protected if VOICE_TOKEN set)
# -----------------------------
@app.post("/voice_trigger")
def voice_trigger():
    # Optional header token to restrict access
    if VOICE_TOKEN and request.headers.get("X-Voice-Token") != VOICE_TOKEN:
        return jsonify(ok=False, rc=401, err="unauthorized"), 401

    # Accept JSON or form payloads; never fails the endpoint (baseline 200)
    try:
        payload = request.get_json(silent=True) or request.form.to_dict() or {}
    except Exception:
        payload = {}

    # Log every invocation (date-rotated file)
    logline = {
        "ts": now_iso(),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "ua": request.headers.get("User-Agent", ""),
        "keys": sorted(list(payload.keys()))
    }
    append_log(dated_log_path(REMD, "voice_trigger"), json.dumps(logline, ensure_ascii=False))

    # Optional: send an SMS only if explicitly allowed and guard is available
    send_status = {"status": "skipped"}
    if ALLOW_SEND and send_sms and TWILIO_TO and TWILIO_FROM:
        try:
            body = f"voice_trigger ping {logline['ts']}"
            send_status = send_sms(body=body, to=TWILIO_TO, from_=TWILIO_FROM, tag="voice")
        except Exception as e:
            send_status = {"status": "error", "reason": str(e)}

    return jsonify(ok=True, ts=logline["ts"], send=send_status), 200

# -----------------------------
# /geo  (token-protected; integer accuracy to engine)
# -----------------------------
@app.get("/geo")
def geo():
    token = request.args.get("token", "")
    if not GEO_TOKEN or token != GEO_TOKEN:
        return jsonify(ok=False, rc=401, err="unauthorized"), 401

    try:
        lat = float(request.args["lat"])
        lon = float(request.args["lon"])
        acc_raw = request.args.get("acc", "50")
        acc_f = float(acc_raw)
        acc_i = int(round(acc_f))  # engine expects integer accuracy
        src = request.args.get("src", "http")
    except Exception:
        return jsonify(ok=False, rc=400, err="lat/lon required"), 400

    engine = BASE / "tools" / "geofence_engine.py"
    if engine.exists():
        cmd = ["python3", str(engine), "--lat", str(lat), "--lon", str(lon),
               "--acc", str(acc_i), "--source", src]
        rc, out, err = run(cmd)
    else:
        rc, out, err = 0, "engine_missing", ""

    # Append an HTTP ingest trace (date-rotated)
    append_log(
        dated_log_path(GEOD, "http_ingest"),
        f"[{now_iso()}] lat={lat} lon={lon} acc={acc_f}({acc_i}) src={src} rc={rc} out={out} err={err}"
    )

    return jsonify(ok=(rc == 0), rc=rc, out=out, err=err, ts=now_iso(), acc_used=acc_i)

# -----------------------------
# /voice/status
# -----------------------------
@app.get("/voice/status")
def voice_status():
    hb = LOGD/"heartbeat"/"memory_absorption_heartbeat.log"
    last_absorb = None; idx_count = None
    if hb.exists():
        try:
            last = hb.read_text(encoding="utf-8").strip().splitlines()[-1]
            if last.startswith("[") and "]" in last:
                last_absorb = last.split("]")[0][1:]
            if "indexed=" in last:
                idx_count = int(last.split("indexed=")[1].split()[0].strip().rstrip(","))
        except Exception:
            pass

    rc, out, err = run(["git", "log", "-1", "--format=%H %cI %s", "--", "memory/"])
    last_git = out if rc == 0 else None
    return jsonify(ok=True, last_absorption_iso=last_absorb,
                   approx_indexed_files=idx_count, last_github_update=last_git)

# -----------------------------
# /ask?q=...
# -----------------------------
@app.get("/ask")
def ask():
    q = (request.args.get("q", "") or "").strip().lower()
    if not q:
        return jsonify(ok=False, rc=400, err="missing q"), 400

    idx = MEM/"index"/"search_index.json"
    if not idx.exists():
        return jsonify(ok=False, rc=503, err="index missing"), 503

    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify(ok=False, rc=500, err=f"bad index: {e}"), 500

    hits = []
    for item in data.get("manifest", []):
        text = " ".join([
            str(item.get("title", "")),
            " ".join(item.get("keywords", [])),
            item.get("path", "")
        ]).lower()
        score = sum(text.count(tok) for tok in q.split() if tok)
        if score > 0:
            hits.append({
                "path": item.get("path", ""),
                "title": item.get("title", ""),
                "score": score
            })
    hits.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(ok=True, query=q, results=hits[:10])

# -----------------------------
# /remind?text=...&when=...
# -----------------------------
@app.get("/remind")
def remind():
    text = request.args.get("text", "").strip()
    when = request.args.get("when", "").strip()
    if not text or not when:
        return jsonify(ok=False, rc=400, err="text and when required"), 400
    script = BASE / "tools" / "remind.py"
    if not script.exists():
        return jsonify(ok=False, rc=503, err="remind.py missing"), 503
    rc, out, err = run(["python3", str(script), "--text", text, "--when", when])
    return jsonify(ok=(rc == 0), rc=rc, out=out, err=err)

# ---- WSGI entry point for PythonAnywhere
application = app

if __name__ == "__main__":
    # Local debugging only; PythonAnywhere uses WSGI
    app.run(host="0.0.0.0", port=8000, debug=True)
