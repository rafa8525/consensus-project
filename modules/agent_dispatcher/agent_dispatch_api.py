# agent_dispatch_api.py
from flask import Flask, request, jsonify
from agent_dispatcher import dispatch_agent, route_to_agent, load_manifest

app = Flask(__name__)
manifest = load_manifest()

@app.route("/dispatch", methods=["POST"])
def dispatch():
    data = request.get_json()
    prompt = data.get("prompt", "")
    agents = data.get("agents", [])

    results = []
    for agent in agents:
        if any(a["name"] == agent for a in manifest):
            response = route_to_agent(agent, prompt)
            results.append({"agent": agent, "response": response})

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True, port=5050)
