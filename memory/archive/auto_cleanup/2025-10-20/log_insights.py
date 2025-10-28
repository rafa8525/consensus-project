import os
import json
import re

log_dir = "logs"
output_file = "web/chart_data.json"

agent_counts = {}

# Pattern matches "planner ran 3 tasks"
pattern = re.compile(r"\] (\w+) (?:ran|confirmed|fetched|executed|processed) (\d+)")

for filename in os.listdir(log_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(log_dir, filename), "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    agent = match.group(1).lower()
                    count = int(match.group(2))
                    agent_counts[agent] = agent_counts.get(agent, 0) + count

# Write to chart_data.json
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(agent_counts, f, indent=2)

print("✅ Chart data updated:", agent_counts)
