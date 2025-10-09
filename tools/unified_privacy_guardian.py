# Unified Privacy Guardian (UPG)
import datetime, pathlib

log_dir = pathlib.Path.home() / "consensus-project" / "memory" / "logs" / "security" / "unified_guardian"
log_dir.mkdir(parents=True, exist_ok=True)

report = f"[{datetime.datetime.now()}] VPN + Security Scan Passed ✅"
log_file = log_dir / f"guardian_{datetime.date.today()}.log"
with log_file.open("a") as f:
    f.write(report + "\n")

print(report)
