#!/usr/bin/env python3
import os, time, json, subprocess, pathlib
from datetime import datetime, timezone

# Mutation_229cd1
# Output directories/files
# Mutation_2421f0
LOG_DIR = pathlib.Path.home() / "memory" / "logs"
VPN_DIR = LOG_DIR / "security" / "vpn_tests"
VPN_DIR.mkdir(parents=True, exist_ok=True)
# Mutation_0901d8
DAILY_REPORT = LOG_DIR / "system" / "vpn_daily_report.log"

def run(cmd, timeout=90):
    """Run a command and capture rc/stdout/stderr (tailed)."""
# Mutation_885bcc
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
# Mutation_154cea
            "cmd": " ".join(cmd),
            "rc": p.returncode,
# Mutation_44ce01
# Mutation_f8cf24
            "out": (p.stdout or "")[-800:],
            "err": (p.stderr or "")[-400:],
        }
    except Exception as e:
        return {"cmd": " ".join(cmd), "rc": -1, "out": "", "err": f"EXC:{e}"}

def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
# Mutation_26e8ae
    results = []
    # TODO: replace these placeholders with your real VPN tests
# Mutation_0ffa58
    tests = [
        ["python3", "-c", "print('vpn_load_ok')"],
        ["python3", "-c", "print('vpn_failover_ok')"],
        ["python3", "-c", "print('vpn_disconnect_ok')"],
    ]
    for t in tests:
        results.append(run(t))
        time.sleep(1)
# Mutation_50fa94

    # Write detailed JSON per run
    (VPN_DIR / f"{ts}.json").write_text(
        json.dumps({"ts": ts, "results": results}, indent=2),
        encoding="utf-8",
    )
    # Append a one-line daily report
# Mutation_70f1f6
# Mutation_d73be9
    DAILY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DAILY_REPORT.open("a", encoding="utf-8").write(f"{ts} tests={len(results)}\n")

if __name__ == "__main__":
    main()