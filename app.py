# app.py — single-file bridge for ChatGPT Voice ↔ your backend
# Endpoints:
#   GET /geo            -> ingest a location ping (uses GEO_TOKEN)
#   GET /voice/status   -> last absorption + last GitHub memory update
#   GET /ask            -> simple memory Q&A over search_index.json
#   GET /remind         -> schedule a reminder (text, when)
#   GET /health         -> quick system sanity

import os, json, subprocess, time
from pathlib import Path
from flask import Flask, request, jsonify
from datetime import datetime, timezone

BASE = Path.home() / "consensus-project"
MEM  = BASE / "memory"
LOGD = MEM / "logs"
GEOD = LOGD / "geofencing"

app = Flask(__name__)
app.url_map.strict_slashes = False  # accept /geo and /geo/

# ---- Hardcoded token (per your request). Env var can still override if set.
GEO_TOKEN = os.environ.get("GEO_TOKEN", "bvJkujAO1MOtHL6WL5RhbdayMEF7ILBnIy4OFzXzkgg")

def run(cmd):
    p = subprocess.Popen(
        cmd, cwd=str(BASE),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = p.communicate(timeout=60)
    return p.returncode, out.strip(), err.strip()

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# -----------------------------
# /geo  (token-protected)
# -----------------------------
@app.get("/geo")
def geo():
    token = request.args.get("token","")
    if not GEO_TOKEN or token != GEO_TOKEN:
        return jsonify(ok=False, rc=401, err="unauthorized"), 401

    try:
        lat = float(request.args["lat"]); lon = float(request.args["lon"])
        acc = float(request.args.get("acc","50"))
        src = request.args.get("src","http")
    except Exception:
        return jsonify(ok=False, rc=400, err="lat/lon required"), 400

    # Call the engine (writes geofence_events.log, etc.)
    cmd = ["python3","tools/geofence_engine.py","--lat",str(lat),"--lon",str(lon),
           "--acc",str(acc),"--source",src]
    rc, out, err = run(cmd)

    # Append an HTTP ingest trace
    GEOD.mkdir(parents=True, exist_ok=True)
    (GEOD/"http_ingest.log").open("a", encoding="utf-8").write(
        f"[{now_iso()}] lat={lat} lon={lon} acc={acc} src={src} rc={rc} out={out} err={err}\n"
    )

    return jsonify(ok=(rc==0), rc=rc, out=out, err=err, ts=now_iso())

# -----------------------------
# /voice/status
# -----------------------------
@app.get("/voice/status")
def voice_status():
    # Last absorption (from heartbeat)
    hb = LOGD/"heartbeat"/"memory_absorption_heartbeat.log"
    last_absorb = None; idx_count = None
    if hb.exists():
        try:
            last = hb.read_text(encoding="utf-8").strip().splitlines()[-1]
            # e.g. "[2025-08-12T16:40:25Z] indexed=458 elapsed=7.26s"
            if last.startswith("[") and "]" in last:
                last_absorb = last.split("]")[0][1:]
            if "indexed=" in last:
                idx_count = int(last.split("indexed=")[1].split()[0].strip().rstrip(","))
        except Exception:
            pass

    # Last GitHub update touching memory/
    rc, out, err = run(["git","log","-1","--format=%H %cI %s","--","memory/"])
    last_git = out if rc==0 else None

    return jsonify(
        ok=True,
        last_absorption_iso=last_absorb,
        approx_indexed_files=idx_count,
        last_github_update=last_git
    )

# -----------------------------
# /ask?q=...
# -----------------------------
@app.get("/ask")
def ask():
    q = (request.args.get("q","") or "").strip().lower()
    if not q:
        return jsonify(ok=False, rc=400, err="missing q"), 400

    idx = MEM/"index"/"search_index.json"
    if not idx.exists():
        return jsonify(ok=False, rc=503, err="index missing"), 503

    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify(ok=False, rc=500, err=f"bad index: {e}"), 500

    # Simple scoring over title+keywords
    hits = []
    for item in data.get("manifest", []):
        text = " ".join([
            str(item.get("title","")),
            " ".join(item.get("keywords", [])),
            item.get("path","")
        ]).lower()
        score = sum(text.count(tok) for tok in q.split())
        if score > 0:
            hits.append({
                "path": item.get("path",""),
                "title": item.get("title",""),
                "score": score
            })
    hits.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(ok=True, query=q, results=hits[:10])

# -----------------------------
# /remind?text=...&when=...
# -----------------------------
@app.get("/remind")
def remind():
    text = request.args.get("text","").strip()
    when = request.args.get("when","").strip()
    if not text or not when:
        return jsonify(ok=False, rc=400, err="text and when required"), 400
    rc, out, err = run(["python3","tools/remind.py","--text",text,"--when",when])
    return jsonify(ok=(rc==0), rc=rc, out=out, err=err)

# -----------------------------
# /health
# -----------------------------
@app.get("/health")
def health():
    status = {"time": now_iso()}
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
    gf_hb = GEOD/f"heartbeat_{today}.md"
    status["geofence_heartbeat_today"] = gf_hb.exists()

    return jsonify(ok=True, **status)

# WSGI entry point for PythonAnywhere
application = app

if __name__ == "__main__":
    # Local debugging only; PythonAnywhere uses WSGI
    app.run(host="0.0.0.0", port=8000, debug=True)
