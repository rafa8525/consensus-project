
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/dispatch', methods=['POST'])
def dispatch():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        agents = data.get('agents', [])
        if not prompt or not agents:
            return jsonify({"error": "Prompt and agents are required"}), 400

        results = {agent: f"{agent} received: {prompt}" for agent in agents}
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5050)
