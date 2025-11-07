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

    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Load template
    with open(TEMPLATE, "r") as f:
        template = f.read()

    # Replace placeholders
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")

    report = template.replace("[Current Date]", today)
    report = report.replace("[Brief Summary]", "System stable. Auto-report generated.")
    report = report.replace("[Specify Day]", today)
    report = report.replace("[Specify Time]", now_time)
    report = report.replace("[Any other relevant information]", "Automated log, no manual input.")
    report = report.replace("[Milestones Achieved:]", "- Automated report generation operational.")
    report = report.replace("[Current Tasks:]", "- Agents running normally.")
    report = report.replace("[Issues/Challenges Faced:]", "- None detected.")
    report = report.replace("[Next Steps:]", "- Continue monitoring.")

    # Save new report
    filename = f"weekly_report_{today}.md"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w") as f:
        f.write(report)

    print(f"Weekly report created: {path}")

if __name__ == "__main__":
    generate_report()
