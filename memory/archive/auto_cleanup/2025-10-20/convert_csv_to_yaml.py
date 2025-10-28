#!/usr/bin/env python3
import csv, yaml, pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
csv_file = BASE / "config" / "55_Agents___Support_Sites.csv"
yaml_file = BASE / "config" / "CONSENSUS_REGISTRY.yaml"

agents = []
with open(csv_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        agents.append({
            "id": row.get("Agent ID") or row.get("ID") or f"Agent_{len(agents)+1}",
            "name": row.get("Agent Name") or row.get("Name") or f"Agent_{len(agents)+1}",
            "role": row.get("Role") or "Unspecified",
            "description": row.get("Description") or "No description"
        })

with open(yaml_file, "w", encoding="utf-8") as f:
    yaml.dump({"agents": agents}, f, sort_keys=False, allow_unicode=True)

print(f"[OK] Wrote {yaml_file} with {len(agents)} agents")
