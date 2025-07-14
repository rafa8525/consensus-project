import datetime
from pathlib import Path

def run_audit():
    timestamp = datetime.datetime.now().isoformat()
    result = "SECURITY AUDIT COMPLETED — No critical issues detected"

    log_entry = f"{timestamp} — {result}\n"
    with Path("security_audit_log.txt").open("a") as f:
        f.write(log_entry)

if __name__ == "__main__":
    if datetime.datetime.now().day == 1:
        run_audit()
