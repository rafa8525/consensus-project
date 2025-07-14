from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
INDEX_PATH = "memory/index/memory_word_index.json"

@app.route("/query_memory_index", methods=["POST"])
def query_memory_index():
    if not os.path.exists(INDEX_PATH):
        return jsonify({"error": "Memory index not found."}), 404

    data = request.get_json()
    question = data.get("query", "").lower()
    keywords = [word.strip(".,!?") for word in question.split()]
    top_only = data.get("top_match_only", False)

    with open(INDEX_PATH, "r") as f:
        memory = json.load(f)

    matches = {}
    for path, content in memory.items():
        if any(kw in content.lower() for kw in keywords):
            matches[path] = content

    if not matches:
        return jsonify({"response": "No relevant memory found."})

    if top_only:
        best_path = sorted(matches.keys())[0]
        return jsonify({"top_match": best_path, "content": matches[best_path]})

    return jsonify(matches)

if __name__ == "__main__":
    app.run()