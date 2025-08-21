# app.py
# Flask app for Consensus Project (PythonAnywhere)
# - Stable /metrics + /memory/absorb
# - Voice endpoints: /voice/last_absorb, /voice/barcode_* (+ _status, _selftest, _map, _explode)
# - Single global JSON error handler scoped to /voice/* only (no after_request mutation)

import os, json, subprocess, re
from datetime import datetime, timezone, date
from pathlib import Path
from flask import Flask, request, Response
try:
    from werkzeug.exceptions import HTTPException  # type: ignore
except Exception:
    HTTPException = None  # fallback

# -------------------------------------------------------------------
# App & constants
# -------------------------------------------------------------------
app = Flask(__name__)

ROOT = Path.home() / "consensus-project"
LOGS = ROOT / "memory" / "logs"
HEARTBEAT = LOGS / "heartbeat"
AGENTS_HEARTBEAT = LOGS / "agents" / "heartbeat"
NUT = LOGS / "nutrition"
BARCODE_CACHE = NUT / "barcode_cache.json"
ABSORB_STATE = HEARTBEAT / "last_absorb_state.json"  # persistent absorb info
HEARTBEAT.mkdir(parents=True, exist_ok=True)
AGENTS_HEARTBEAT.mkdir(parents=True, exist_ok=True)
NUT.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _read_token() -> str:
    try:
        cfg = json.loads((Path.home()/".pa_env.json").read_text())
        return str(cfg.get("VOICE_TOKEN","")).strip()
    except Exception:
        return ""

def _voice_guard() -> bool:
    stored = _read_token()
    sent = request.headers.get("X-Voice-Token","").strip()
    return bool(stored) and stored == sent

def _voice_debug() -> bool:
    v = request.headers.get("X-Debug","")
    return str(v).strip().lower() in {"1","true","yes","on"}

def _voice_json(payload: dict, status: int = 200) -> Response:
    # Always produce JSON Response (no jsonify) to avoid proxy quirks
    return Response(json.dumps(payload, ensure_ascii=False), status=status, mimetype="application/json")

def _log_voice_error(e: Exception) -> None:
    try:
        import traceback as tb
        path = ""
        try: path = request.path
        except Exception: pass
        AGENTS_HEARTBEAT.mkdir(parents=True, exist_ok=True)
        with (AGENTS_HEARTBEAT / f"voice_errors_{date.today().isoformat()}.log").open("a", encoding="utf-8") as f:
            f.write(f"[{_utcnow_iso()}] {path}: {e}\n{tb.format_exc()}\n")
    except Exception:
        pass

def _git_version() -> str:
    try:
        sha = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
        line = subprocess.check_output(["git","show","-s","--format=%cI %s","HEAD"], cwd=ROOT, text=True).strip()
        return f"{sha} {line}"
    except Exception:
        return "unknown"

def _read_absorb_state() -> dict:
    try:
        return json.loads(ABSORB_STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"ts":"", "hits_today":0, "date":""}

def _write_absorb_state(ts_iso: str) -> dict:
    today = date.today().isoformat()
    st = _read_absorb_state()
    if st.get("date") == today:
        hits = int(st.get("hits_today",0)) + 1
    else:
        hits = 1
    new = {"ts": ts_iso, "hits_today": hits, "date": today}
    ABSORB_STATE.write_text(json.dumps(new, indent=2), encoding="utf-8")
    return new

# -------------------------------------------------------------------
# Metrics & Absorb
# -------------------------------------------------------------------
@app.route("/metrics", methods=["GET"])
def metrics():
    st = _read_absorb_state()
    return _voice_json({
        "last_memory_absorb_iso": st.get("ts",""),
        "memory_absorb_hits_today": st.get("hits_today", 0),
        "version": _git_version(),
    }, 200)

@app.route("/memory/absorb", methods=["POST","GET"])
def memory_absorb():
    # Keep token-gated to prevent abuse (same token as voice)
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    now = _utcnow_iso()
    st = _write_absorb_state(now)
    # Include HEAD commit ref for your absorb_guard logs
    try:
        commit = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    return _voice_json({"ok": True, "commit": commit, "ts": st["ts"], "hits_today": st["hits_today"]}, 200)

# -------------------------------------------------------------------
# Voice: last_absorb (reads metrics)
# -------------------------------------------------------------------
@app.route("/voice/last_absorb", methods=["GET"])
def voice_last_absorb():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    st = _read_absorb_state()
    ts = st.get("ts","")
    hits = int(st.get("hits_today",0))
    text = f"The latest GitHub memory absorb was at {ts} UTC. Absorbs today: {hits}." if ts else \
           "I don't have a recorded GitHub memory absorb yet."
    return _voice_json({"ok": True, "ts": ts, "hits_today": hits, "text": text}, 200)

# -------------------------------------------------------------------
# Voice: Barcode helpers
# -------------------------------------------------------------------
def _try_refresh_cache():
    if BARCODE_CACHE.exists():
        return
    # Best-effort refresh (non-fatal)
    try:
        subprocess.check_call(["python3","tools/barcode_cache.py"], cwd=ROOT)
    except Exception:
        pass

def _load_cache() -> list:
    _try_refresh_cache()
    try:
        return json.loads(BARCODE_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _summarize(records: list) -> str:
    try:
        records = records or []
        n = len(records)
        keto = sum(1 for r in records if (r.get("class","").lower().startswith("keto")))
        slightly = sum(1 for r in records if (r.get("class","").lower().startswith("slightly")))
        nonfood = 0
        nf_re = re.compile(r"(tissue|towel|sanitizer|soap|detergent|shampoo|deodorant|lotion|trash bag)", re.I)
        for r in records:
            if nf_re.search((r.get("item") or "") + " " + (r.get("details") or "")):
                nonfood += 1
        seen, last_items = set(), []
        for r in reversed(records):
            it = (r.get("item") or "(unknown)").strip()
            if it and it not in seen:
                last_items.append(it); seen.add(it)
            if len(last_items) == 10: break
        msg = f"I have {n} cached barcode rows. Keto-tagged: {keto}, Slightly Keto: {slightly}, non-food: {nonfood}."
        if last_items:
            tail = ", ".join(last_items[:5]) + ("" if len(last_items) <= 5 else ", ...")
            msg += " Recent items: " + tail
        return msg
    except Exception:
        return "I have a cached barcode snapshot, but summarizing it failed."

def _lookup(records: list, q: str) -> list:
    q = (q or "").strip().lower()
    if not q: return []
    toks = q.split()
    hits = []
    for r in reversed(records):
        hay = " ".join([r.get("item",""), r.get("details",""), r.get("class","")]).lower()
        if all(t in hay for t in toks):
            hits.append(r)
        if len(hits) >= 50:
            break
    return hits

# -------------------------------------------------------------------
# Voice: Barcode routes
# -------------------------------------------------------------------
@app.route("/voice/barcode_summary", methods=["GET"])
def voice_barcode_summary():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    recs = _load_cache()
    text = _summarize(recs) if recs else "I don't have a cached barcode snapshot yet."
    return _voice_json({"ok": True, "text": text, "ts": _utcnow_iso()}, 200)

@app.route("/voice/barcode_lookup", methods=["GET"])
def voice_barcode_lookup():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    q = request.args.get("q","")
    recs = _load_cache()
    if not q.strip():
        return _voice_json({"ok": True, "text": "No query provided.", "count": 0, "items": []}, 200)
    hits = _lookup(recs, q)
    if not hits:
        return _voice_json({"ok": True, "text": f"No matches for '{q}'.", "count": 0, "items": []}, 200)
    names = []
    for r in hits[:5]:
        k = (r.get("class") or "").strip()
        names.append(f"{r.get('item','(unknown)')}{(' ['+k+']') if k else ''}")
    line = f"Found {len(hits)} match(es). Top: " + "; ".join(names) + "."
    return _voice_json({"ok": True, "text": line, "count": len(hits), "items": hits}, 200)

@app.route("/voice/barcode_probe", methods=["GET"])
def voice_barcode_probe():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    recs = _load_cache()
    return _voice_json({"ok": True, "count": len(recs), "has_cache": bool(recs), "sample": recs[:2]}, 200)

@app.route("/voice/_status", methods=["GET"])
def voice_status():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    recs = _load_cache()
    return _voice_json({
        "ok": True,
        "routes": ["_status","_selftest","_map","barcode_probe","barcode_summary","barcode_lookup","last_absorb"],
        "cache_rows": len(recs),
        "now": _utcnow_iso()
    }, 200)

@app.route("/voice/_selftest", methods=["GET"])
def voice_selftest():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    info = {}
    try:
        info["cache_path"] = str(BARCODE_CACHE)
        info["cache_exists"] = BARCODE_CACHE.exists()
        recs = _load_cache()
        info["cache_len"] = len(recs)
        info["first"] = recs[0] if recs else None
        info["summary_try"] = _summarize(recs)
        return _voice_json({"ok": True, "selftest": info}, 200)
    except Exception as e:
        info["error"] = "server_error"
        _log_voice_error(e)
        return _voice_json({"ok": False, "selftest": info}, 200)

@app.route("/voice/_map", methods=["GET"])
def voice_map():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    try:
        rules = sorted([str(r.rule) for r in app.url_map.iter_rules() if str(r.rule).startswith("/voice/")])
        return _voice_json({"ok": True, "rules": rules}, 200)
    except Exception as e:
        _log_voice_error(e)
        return _voice_json({"ok": False, "error": "server_error"}, 200)

# Debug: intentional error to verify JSON handler (use X-Debug: 1 to reveal reason)
@app.route("/voice/_explode", methods=["GET"])
def voice_explode():
    if not _voice_guard():
        return _voice_json({"ok": False, "error": "unauthorized"}, 401)
    raise ValueError("boom for debug")

# -------------------------------------------------------------------
# Single global error handler limited to /voice/*
# -------------------------------------------------------------------
@app.errorhandler(Exception)
def _voice_global_errors(e):
    try:
        path = ""
        try: path = request.path
        except Exception: pass

        # Only intercept voice routes
        if str(path).startswith("/voice/"):
            _log_voice_error(e)
            dbg = _voice_debug()
            reason = str(e) if dbg else "hidden"
            return _voice_json({"ok": False, "error": "server_error", "reason": reason}, 200)

        # Non-voice: default handling
        if HTTPException and isinstance(e, HTTPException):
            return e  # let Flask craft the proper response
        return ("Internal Server Error", 500)
    except Exception:
        # Final safety for voice paths
        try:
            if str(request.path).startswith("/voice/"):
                return _voice_json({"ok": False, "error": "server_error", "reason": "handler_failed"}, 200)
        except Exception:
            pass
        return ("Internal Server Error", 500)

# -------------------------------------------------------------------
# Entry point (for local debug)
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","5000")))

# --- VOICE CLEAN ERROR HANDLERS (BEGIN) ---
from flask import request as _VREQ
@app.errorhandler(Exception)
def _voice_exc(e):
    try:
        if str(getattr(_VREQ, "path", "")).startswith("/voice/"):
            return _voice_json({"ok": False, "error": "server_error"}, 200)
    except Exception:
        pass
    raise e

@app.errorhandler(404)
def _voice_404(e):
    try:
        if str(getattr(_VREQ, "path", "")).startswith("/voice/"):
            return _voice_json({"ok": False, "error": "not_found"}, 200)
    except Exception:
        pass
    return e
# --- VOICE CLEAN ERROR HANDLERS (END) ---
