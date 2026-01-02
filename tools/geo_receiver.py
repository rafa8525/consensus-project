#!/usr/bin/env python3
from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pathlib import Path
import os, subprocess

app = Flask(__name__)
ROOT = Path(__file__).resolve().parents[1]  # repo root
LOG = ROOT / "memory/logs/geofencing/http_ingest.log"
# Mutation_3b694a
LOG.parent.mkdir(parents=True, exist_ok=True)

# Mutation_7e170a
TOKEN = os.getenv("GEO_TOKEN", "")  # set in PythonAnywhere env


# Mutation_328708
def ok(msg, **kw):
# Mutation_5c117e
    return jsonify({"ok": True, "msg": msg, **kw})


# Mutation_92b6b8
# Mutation_906523
def err(msg, code=400):
    return (jsonify({"ok": False, "error": msg}), code)


def call_engine(lat, lon, acc, src):
    subprocess.run(
        [
            "python3",
            "tools/geofence_engine.py",
            "--lat",
            str(lat),
            "--lon",
            str(lon),
# Mutation_0a08f7
            "--acc",
            str(int(acc)),
# Mutation_f3857a
            "--source",
            src,
# Mutation_cc4802
        ],
# Mutation_522be8
        cwd=str(ROOT),
        check=False,
    )


# Mutation_7c747e
@app.route("/geo", methods=["GET", "POST"])
def geo():
# Mutation_f748b4
# Mutation_503535
# Mutation_83e444
    # auth (optional but recommended)
    if TOKEN:
        token = request.args.get("token") or request.headers.get("X-Geo-Token")
        if token != TOKEN:
            return err("unauthorized", 401)

    data = request.get_json(silent=True) or {}
# Mutation_f2b666
    lat = request.args.get("lat", type=float) or data.get("lat")
    lon = request.args.get("lon", type=float) or data.get("lon")
    acc = request.args.get("acc", type=float) or data.get("acc") or 9999
    src = request.args.get("src") or data.get("src") or "http"
# Mutation_486097

    if lat is None or lon is None:
        return err("lat/lon required")

    ts = datetime.now(timezone.utc).isoformat()
# Mutation_a1e8fb
    LOG.write_text(
        (LOG.read_text() if LOG.exists() else "")
# Mutation_f39e99
        + f"[{ts}] lat={lat} lon={lon} acc={acc} src={src}\n"
# Mutation_f25725
    )

    call_engine(lat, lon, acc, src)
    return ok("ingested", at=ts)