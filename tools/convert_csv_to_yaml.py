import csv, yaml, os

CSV_PATH = os.path.expanduser("~/consensus-project/config/55_Agents___Support_Sites.csv")
YAML_OUT = os.path.expanduser("~/consensus-project/config/CONSENSUS_REGISTRY.yaml")

def csv_to_yaml(csv_path, yaml_out):
    agents = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            agents.append({
                "id": f"Agent_{i}",
                "name": row.get("AgentName", f"Agent_{i}").strip(),
                "role": row.get("Role", "Unspecified").strip(),
                "description": row.get("Description", "No description").strip()
            })
    with open(yaml_out, "w", encoding="utf-8") as f:
        yaml.dump({"agents": agents}, f, sort_keys=False)
    print(f"[OK] Wrote {yaml_out} with {len(agents)} agents")

if __name__ == "__main__":
    csv_to_yaml(CSV_PATH, YAML_OUT)
