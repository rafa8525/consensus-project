#!/usr/bin/env python3
"""
flask_app.py
Merged version:
- Keeps memory lookup + absorption routes
- Adds persistent voice trigger queueing
- Adds WSGI compatibility with `application = app`
"""

from flask import Flask, request, jsonify
from pathlib import Path
import os, subprocess, datetime, json

app = Flask(__name__)

# === Paths ===
LOOKUP_SCRIPT = "/home/rafa1215/memory/tools/voice_memory_lookup.py"
MASTER_LOOP_SCRIPT = "/home/rafa1215/memory/tools/daily_master_loop.py"
LOOKUP_HEARTBEAT_LOG = "/home/rafa1215/consensus-project/memory/logs/heartbeat/voice_lookup_heartbeat.log"

QUEUE_DIR = Path("queue/processing")
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


# === Utility Functions ===
def log_voice_trigger(query, result_status):
    """Log every voice-trigger lookup attempt."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOOKUP_HEARTBEAT_LOG), exist_ok=True)
    with open(LOOKUP_HEARTBEAT_LOG, "a", encoding="utf-8") as log:
        log.write(f"[{now}] Query: '{query}' | Status: {result_status}\n")


def run_lookup(query):
    """Run the memory lookup script with a keyword or filename."""
    try:
        result = subprocess.check_output(
            ["/usr/bin/python3", LOOKUP_SCRIPT, query],
            stderr=subprocess.STDOUT
        ).decode("utf-8", errors="ignore").strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"[ERROR running lookup: {e.output.decode('utf-8', errors='ignore')}]"


def run_absorption():
    """Trigger a fresh memory absorption if lookup fails."""
    try:
        subprocess.run(["/usr/bin/python3", MASTER_LOOP_SCRIPT], check=False)
        return True
    except Exception:
        return False


# === Routes ===
@app.route("/", methods=["GET"])
def home():
    """Root route to verify the API is running."""
    return jsonify({"status": "ok", "message": "Reminder API running"}), 200


@app.route("/voice_trigger", methods=["POST"])
def voice_trigger():
    """
    Handle voice-triggered memory lookups,
    AND enqueue a job for SMS sending (persistent).
    """
    query = request.form.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    # Run lookup
    result = run_lookup(query)

    if "[No results found" in result:
        # Log miss and try a refresh
        log_voice_trigger(query, "NOT FOUND - Triggering absorption")
        run_absorption()
        result = run_lookup(query)
        if "[No results found" in result:
            status = "not_found"
            message = f"I couldn’t find anything for '{query}' even after refreshing."
        else:
            status = "success"
            message = result
    else:
        # Log success
        log_voice_trigger(query, "FOUND")
        status = "success"
        message = result

    # Always enqueue SMS job for persistence
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    job_file = QUEUE_DIR / f"voice_trigger_{ts}.json"
    job = {"type": "sms", "timestamp": ts, "message": f"Voice trigger for '{query}' → {status}"}
    job_file.write_text(json.dumps(job))

    return jsonify({"status": status, "query": query, "result": message})


@app.route("/view_queue", methods=["GET"])
def view_queue():
    """Manual test route to view queued reminders."""
    QUEUE_FILE = os.path.expanduser("~/consensus-project/memory/logs/reminders/pending_reminders.json")
    if not os.path.exists(QUEUE_FILE):
        return jsonify({"status": "empty", "reminders": []}), 200
    with open(QUEUE_FILE, "r") as f:
        try:
            reminders = json.load(f)
        except json.JSONDecodeError:
            reminders = []
    return jsonify({"status": "success", "reminders": reminders}), 200


# === WSGI Compatibility ===
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
