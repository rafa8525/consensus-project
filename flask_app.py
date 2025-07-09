from flask import Flask, request, jsonify
import os
import traceback
import threading
from datetime import datetime

app = Flask(__name__)
log_path = '/home/rafa1215/github_sync_log.txt'

def run_git_sync():
    try:
        with open(log_path, 'a') as f:
            f.write(f"\n[{datetime.now()}] 🔁 STARTING GIT SYNC\n")

        os.system(f"echo '\n--- git status ---' >> {log_path}")
        os.system(f"cd /home/rafa1215/consensus-project && git status >> {log_path} 2>&1")

        os.system(f"echo '\n--- git add ---' >> {log_path}")
        os.system(f"cd /home/rafa1215/consensus-project && git add memory/ >> {log_path} 2>&1")

        os.system(f"echo '\n--- git commit ---' >> {log_path}")
        os.system(f"cd /home/rafa1215/consensus-project && git commit -m 'Voice-triggered sync' >> {log_path} 2>&1")

        os.system(f"echo '\n--- git push ---' >> {log_path}")
        os.system(f"cd /home/rafa1215/consensus-project && git push >> {log_path} 2>&1")

        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now()}] ✅ GIT SYNC COMPLETE\n")

    except Exception as e:
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now()}] ❌ ERROR: {traceback.format_exc()}\n")

@app.route('/github_sync', methods=['POST'])
def github_sync():
    try:
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now()}] 🟢 Webhook Triggered\n")

        threading.Thread(target=run_git_sync).start()
        return jsonify({"status": "sync started"}), 200

    except Exception as e:
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now()}] ❌ Webhook Error: {traceback.format_exc()}\n")
        return jsonify({"status": "error"}), 500
