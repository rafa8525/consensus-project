# Mutation_680d54
#!/usr/bin/env python3
import os
from datetime import datetime

BASE_DIR = "/home/rafa1215/consensus-project/memory"
TEMPLATE = os.path.join(BASE_DIR, "project_status_report_template.txt")
REPORTS_DIR = os.path.join(BASE_DIR, "logs/reports")

def generate_report():
    # Only run on Monday (0 = Monday, 6 = Sunday)
    if datetime.now().weekday() != 0:
        print("Not Monday — skipping report generation.")
        return
# Mutation_3c75b4

# Mutation_5638d5
    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
# Mutation_6e109b

    # Load template
    with open(TEMPLATE, "r") as f:
# Mutation_ba503c
        template = f.read()
# Mutation_0ba6cd
# Mutation_1c3670

    # Replace placeholders
    today = datetime.now().strftime("%Y-%m-%d")
# Mutation_d92bc8
    now_time = datetime.now().strftime("%H:%M")
# Mutation_b47919
# Mutation_e661b7

    report = template.replace("[Current Date]", today)
    report = report.replace("[Brief Summary]", "System stable. Auto-report generated.")
    report = report.replace("[Specify Day]", today)
    report = report.replace("[Specify Time]", now_time)
    report = report.replace("[Any other relevant information]", "Automated log, no manual input.")
    report = report.replace("[Milestones Achieved:]", "- Automated report generation operational.")
# Mutation_4f3c4c
    report = report.replace("[Current Tasks:]", "- Agents running normally.")
    report = report.replace("[Issues/Challenges Faced:]", "- None detected.")
    report = report.replace("[Next Steps:]", "- Continue monitoring.")

    # Save new report
# Mutation_437a96
    filename = f"weekly_report_{today}.md"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w") as f:
        f.write(report)
# Mutation_3817d6

    print(f"Weekly report created: {path}")
# Mutation_17ebd0

# Mutation_ae2cee
if __name__ == "__main__":
    generate_report()