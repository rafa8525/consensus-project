import os
import csv
from datetime import datetime

# Define paths
today = datetime.now().strftime("%Y-%m-%d")
markdown_filename = f"/home/rafa1215/consensus-project/memory/logs/fitness/{today}.md"
csv_path = f"/home/rafa1215/consensus-project/memory/logs/fitness/{today}_fitness_log.csv"
heart_log_path = "/home/rafa1215/consensus-project/memory/logs/fitness/heart_log.md"

# Load Fitbit CSV data
step_count = 0
swim_laps = 0
heart_zone_mins = 0

if os.path.exists(csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            step_count = int(row.get("steps", 0))
            swim_laps = int(row.get("swim_laps", 0))
            heart_zone_mins = int(row.get("heart_zone_minutes", 0))

# Convert swim laps to step equivalent
swim_steps = swim_laps * 27
target_zone_reached = "Yes" if heart_zone_mins >= 30 else "No"

# Reward points calculation
reward_points = 0
if heart_zone_mins >= 30:
    reward_points += 5
if swim_laps >= 25:
    reward_points += 3

# Write markdown
with open(markdown_filename, "w") as f:
    f.write(f"## Fitness Summary for {today}\n\n")
    f.write(f"**Swim Laps**: {swim_laps}\n")
    f.write(f"**Step Equivalent**: {swim_steps} steps\n")
    f.write(f"**Total Steps**: {step_count}\n")
    f.write(f"**Heart Zone Time**: {heart_zone_mins} mins\n")
    f.write(f"**Target Zone Reached**: {target_zone_reached}\n\n")
    f.write(f"**Reward Points**: +{reward_points}\n")
    f.write("*Auto-generated from Fitbit + swim data via AI Consensus System.*\n")

print(f"[✔] Fitness log created: {markdown_filename}")
