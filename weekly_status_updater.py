import datetime
import sys
from pathlib import Path

# ✅ Only run on Mondays (0 = Monday)
if datetime.datetime.today().weekday() != 0:
    sys.exit(0)

def get_last_vpn_log():
    log_path = Path("vpn_activation_log.txt")
    if log_path.exists():
        return log_path.read_text().strip().splitlines()[-1]
    return "No VPN activity logged yet."

def update_status_report():
    today = datetime.date.today().isoformat()
    vpn_log = get_last_vpn_log()

    report = (
        f"Project Name: AutoConnectVPN Implementation\n"
        f"Date: {today}\n\n"
        "Progress Update:\n"
        "- Milestones Achieved:\n"
        "  - VPN triggers on public Wi-Fi detection\n"
        "  - VPN testing plans documented (load, concurrency, failover)\n"
        "  - Initial activation feature deployed\n\n"
        "- Current Tasks:\n"
        "  - Execute all pending VPN tests (failover, endurance, etc.)\n"
        "  - Improve fallback logic and public network detection accuracy\n\n"
        "- Issues/Challenges Faced:\n"
        "  - Public Wi-Fi detection is still limited to SSID-based matching\n"
        "  - No recent test logs uploaded since initial integration\n\n"
        "- Next Steps:\n"
        "  - Run stress + endurance tests\n"
        "  - Complete fallback safety triggers\n\n"
        "Overall Status: IN PROGRESS\n\n"
        "Additional Notes:\n"
        "- Weekly updates now automated and tied to this report\n"
        f"- Most recent VPN activation log:\n  {vpn_log}\n"
    )

    Path("project_status_report_template.txt").write_text(report)

def update_audit_schedule():
    today = datetime.date.today()
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    audit_text = f"""Security Audit Schedule

Frequency: Monthly  
Purpose: To assess and enhance the security measures of the AI Consensus System  
Tasks:
- Conduct thorough security checks
- Identify vulnerabilities and risks
- Implement necessary security enhancements

Next Audit Date: {next_month}
"""
    Path("security_audit_schedule.txt").write_text(audit_text)

# Run both tasks
update_status_report()
update_audit_schedule()
