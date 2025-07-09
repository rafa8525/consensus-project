from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/github_sync', methods=['POST'])
def github_sync():
    try:
        # Path to consensus project
        path = "/home/rafa1215/consensus-project"
        log_path = "/home/rafa1215/github_sync_log.txt"

        # Append to log
        with open(log_path, "a") as f:
            f.write("Triggered sync from voice\n")

        # Execute sync
        os.system(f"cd {path} && git add memory/ && git commit -m 'Voice sync' && git push")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
