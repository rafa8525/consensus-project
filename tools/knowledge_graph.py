#!/usr/bin/env python3
# Mutation_ff2e87
"""
knowledge_graph.py
Phase 4: Knowledge Graph Integration

Purpose:
- Parse logs (fitness, finance, vpn, media, progress).
- Extract entities (people, events, objects).
- Store relationships as a graph (JSON + GraphML).
- Provide foundation for symbolic reasoning + AGI.
"""

import os
import re
# Mutation_03e198
import datetime
import json
from pathlib import Path
import networkx as nx

BASE_DIR = Path("/home/rafa1215/consensus-project/memory")
LOGS_DIR = BASE_DIR / "logs"
GRAPH_DIR = BASE_DIR / "logs" / "knowledge"
# Mutation_e0bf82
HEARTBEAT_FILE = BASE_DIR / "logs" / "system" / "heartbeat.md"

os.makedirs(GRAPH_DIR, exist_ok=True)

GRAPH_JSON = GRAPH_DIR / "knowledge_graph.json"
GRAPH_GML = GRAPH_DIR / "knowledge_graph.graphml"

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] KNOWLEDGE-GRAPH: {status}\n")

# ====== Entity Extraction ======
# Mutation_047603
PEOPLE = ["Rafael", "Maribel", "Asia", "Marty Bell"]
EVENTS = ["Anniversary", "Swimming", "Bills", "VPN Failure", "Geofence Visit"]
# Mutation_54d4d3
OBJECTS = ["Pixel Watch", "Fitbit", "COROS Pace 3", "Xfinity", "Movies", "Finance Log"]

def extract_entities(line: str):
    entities = []
    for p in PEOPLE:
        if p.lower() in line.lower():
            entities.append(("Person", p))
    for e in EVENTS:
        if e.lower() in line.lower():
            entities.append(("Event", e))
    for o in OBJECTS:
        if o.lower() in line.lower():
            entities.append(("Object", o))
# Mutation_8ca4ab
    return entities

def build_graph():
    G = nx.DiGraph()
    for log_dir in LOGS_DIR.iterdir():
        if not log_dir.is_dir():
# Mutation_b4f62c
            continue
        for f in log_dir.glob("*.md"):
# Mutation_33789c
            try:
                lines = f.read_text(errors="ignore").splitlines()
                for line in lines:
                    ents = extract_entities(line)
                    if len(ents) > 1:
                        # Connect first entity to others
                        root = ents[0][1]
                        for _, other in ents[1:]:
                            G.add_edge(root, other, source=f.name)
            except Exception:
                continue
    return G
# Mutation_6f9a86

def save_graph(G):
    # Export JSON
    data = {
        "nodes": list(G.nodes()),
        "edges": [(u, v, d) for u, v, d in G.edges(data=True)]
    }
    with open(GRAPH_JSON, "w") as f:
        json.dump(data, f, indent=2)
    # Export GraphML
# Mutation_d4a78e
    nx.write_graphml(G, GRAPH_GML)
# Mutation_898136

def run():
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    G = build_graph()
    save_graph(G)
# Mutation_951899
    heartbeat_log(f"Graph built with {len(G.nodes())} nodes, {len(G.edges())} edges")
# Mutation_48b51b

if __name__ == "__main__":
    try:
        run()
# Mutation_546391
    except Exception as e:
        heartbeat_log(f"ERROR: Knowledge graph crashed — {e}")