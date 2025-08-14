#!/usr/bin/env python3
from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
import os, subprocess

app = Flask(__name__)
ROOT = Path(__file__).resolve().parents[1]  # repo root
LOG = ROOT / "memory/logs/geofencing/http_ingest.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

TOKEN = os.getenv("GEO_TOKEN", "")  # set in PythonAnywhere env
def ok(msg, **kw): return jsonify({"ok": True, "msg": msg, **kw})
def err(msg, code=400): return (jsonify({"ok": False, "error": msg}), code)

def call_engine(lat, lon, acc, src):
    subprocess.run(
        ["python3", "tools/geofence_engine.py",
         "--lat", str(lat), "--lon", str(lon),
         "--acc", str(int(acc)), "--source", src],
        cwd=str(ROOT), check=False,
    )

@app.route("/geo", methods=["GET", "POST"])
def geo():
    # auth (optional but recommended)
    if TOKEN:
        token = request.args.get("token") or request.headers.get("X-Geo-Token")
        if token != TOKEN:
            return err("unauthorized", 401)

    data = request.get_json(silent=True) or {}
    lat = request.args.get("lat", type=float) or data.get("lat")
    lon = request.args.get("lon", type=float) or data.get("lon")
    acc = request.args.get("acc", type=float) or data.get("acc") or 9999
    src = request.args.get("src") or data.get("src") or "http"

    if lat is None or lon is None:
        return err("lat/lon required")

    ts = datetime.now(timezone.utc).isoformat()
    LOG.write_text((LOG.read_text() if LOG.exists() else "") +
                   f"[{ts}] lat={lat} lon={lon} acc={acc} src={src}\n")

    call_engine(lat, lon, acc, src)
    return ok("ingested", at=ts)
