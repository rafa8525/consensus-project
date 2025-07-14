import datetime
from pathlib import Path

def vpn_fallback_check():
    date_str = datetime.date.today().isoformat()
    log_file = Path("vpn_activation_log.txt")
    fallback_file = Path("memory/logs/security/vpn_fallback_" + date_str + ".md")
    timestamp = datetime.datetime.now().isoformat()

    try:
        logs = log_file.read_text().splitlines()
        today_logs = [line for line in logs if date_str in line and "VPN: ACTIVATED" in line]
        if not today_logs:
            fallback_file.parent.mkdir(parents=True, exist_ok=True)
            with fallback_file.open("a") as f:
                f.write(f"{timestamp} — ⚠️ No VPN activation detected for today\n")
    except FileNotFoundError:
        fallback_file.parent.mkdir(parents=True, exist_ok=True)
        with fallback_file.open("a") as f:
            f.write(f"{timestamp} — ⚠️ vpn_activation_log.txt not found\n")

if __name__ == "__main__":
    vpn_fallback_check()
