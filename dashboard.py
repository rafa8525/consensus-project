from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import datetime

app = Flask(__name__, static_url_path='', static_folder='web')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/save-goal', methods=['POST'])
def save_goal():
    goal = request.form.get('goal')
    with open("scheduled_goal.txt", "w") as f:
        f.write(goal)
    return "Goal saved"

@app.route('/goal')
def get_goal():
    try:
        with open("scheduled_goal.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

@app.route('/digest')
def get_digest():
    try:
        with open("logs/daily_digest.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No digest available."

@app.route('/download-digest')
def download_digest():
    return send_from_directory('logs', 'daily_digest.txt', as_attachment=True)

@app.route('/chart-data')
def chart_data():
    try:
        with open("web/chart_data.json", "r") as f:
            return f.read(), 200, {"Content-Type": "application/json"}
    except FileNotFoundError:
        return "{}", 200, {"Content-Type": "application/json"}

@app.route('/memory-logs')
def memory_logs():
    memory_dir = 'memory'
    logs = [f for f in os.listdir(memory_dir) if f.startswith("memory_log_") and f.endswith(".txt")]
    return jsonify(logs)

@app.route('/memory/<filename>')
def load_memory_log(filename):
    try:
        with open(f"memory/{filename}", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "File not found.", 404

@app.route('/logs/current')
def live_log():
    try:
        with open("logs/current_log.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No logs available."

if __name__ == '__main__':
    app.run(port=8000, debug=True)
