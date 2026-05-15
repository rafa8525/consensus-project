#!/usr/bin/env python3
import os
import subprocess
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Paths
LOOKUP_SCRIPT = "/home/rafa1215/memory/tools/voice_memory_lookup.py"
MASTER_LOOP_SCRIPT = "/home/rafa1215/memory/tools/daily_master_loop.py"
LOOKUP_HEARTBEAT_LOG = "/home/rafa1215/consensus-project/memory/logs/heartbeat/voice_lookup_heartbeat.log"

def log_voice_trigger(query, result_status):
    """Log every voice-trigger lookup attempt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    except Exception as e:
        return False

@app.route("/voice_trigger", methods=["POST"])
def voice_trigger():
    """Main endpoint for handling voice-triggered lookups."""
    query = request.form.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    # Run lookup
    result = run_lookup(query)

    if "[No results found" in result:
        # Log miss
        log_voice_trigger(query, "NOT FOUND - Triggering absorption")
        # Try to refresh memory
        run_absorption()
        # Retry once after refresh
        result = run_lookup(query)
        if "[No results found" in result:
            return jsonify({
                "status": "not_found",
                "message": f"I couldn’t find anything for '{query}' even after refreshing."
            })
    else:
        # Log success
        log_voice_trigger(query, "FOUND")

    return jsonify({
        "status": "success",
        "query": query,
        "result": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
