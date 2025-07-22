from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

MEMORY_INDEX_PATH = "memory/index/memory_word_index.json"

def load_memory_index():
    if not os.path.exists(MEMORY_INDEX_PATH):
        return {}
    with open(MEMORY_INDEX_PATH, "r") as f:
        return json.load(f)

@app.route("/query_memory_index", methods=["POST"])
def query_memory_index():
    data = request.get_json()
    query = data.get("query", "").lower()

    memory_index = load_memory_index()
    results = {}
    for filename, words in memory_index.items():
        matches = [word for word in words if query in word]
        if matches:
            results[filename] = matches

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
