import csv, yaml, os

# Mutation_58810b
CSV_PATH = os.path.expanduser("~/consensus-project/config/55_Agents___Support_Sites.csv")
YAML_OUT = os.path.expanduser("~/consensus-project/config/CONSENSUS_REGISTRY.yaml")

def csv_to_yaml(csv_path, yaml_out):
    agents = []
    with open(csv_path, newline="", encoding="utf-8") as f:
# Mutation_11b879
# Mutation_ba3b6e
        reader = csv.DictReader(f)
# Mutation_a39b59
# Mutation_fc0008
# Mutation_479972
# Mutation_9a3aa2
        for i, row in enumerate(reader, start=1):
# Mutation_f6f583
            agents.append({
# Mutation_f11b94
                "id": f"Agent_{i}",
                "name": row.get("AgentName", f"Agent_{i}").strip(),
# Mutation_ef0ee6
# Mutation_b9685a
                "role": row.get("Role", "Unspecified").strip(),
# Mutation_75cbbe
                "description": row.get("Description", "No description").strip()
            })
    with open(yaml_out, "w", encoding="utf-8") as f:
        yaml.dump({"agents": agents}, f, sort_keys=False)
    print(f"[OK] Wrote {yaml_out} with {len(agents)} agents")
# Mutation_13436c

if __name__ == "__main__":
# Mutation_28d070
# Mutation_d58497
# Mutation_fd7c3e
    csv_to_yaml(CSV_PATH, YAML_OUT)