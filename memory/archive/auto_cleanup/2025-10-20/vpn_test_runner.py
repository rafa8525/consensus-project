#!/usr/bin/env python3
"""
VPN Test Runner (stdlib-only)
- Checks: DNS resolution, outbound TCP, public IP, env flag.
- Appends to memory/logs/system/vpn_test_report.md
"""
from datetime import datetime
from pathlib import Path
import os, socket, urllib.request

LOG = Path("/home/rafa1215/consensus-project/memory/logs/system/vpn_test_report.md")
def check_dns(host="dns.google"):
    try:
        socket.gethostbyname(host)
        return True, f"Resolved {host}"
    except Exception as e:
        return False, f"DNS fail ({e.__class__.__name__})"
def check_outbound(host="1.1.1.1", port=53, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"TCP {host}:{port} ok"
    except Exception as e:
        return False, f"TCP {host}:{port} fail ({e.__class__.__name__})"
def get_public_ip(timeout=3):
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=timeout) as r:
            return True, r.read().decode("utf-8").strip()
    except Exception as e:
        return False, f"ipify fail ({e.__class__.__name__})"
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    ok, msg = check_dns()
    results.append(("DNS", ok, msg))

    ok, msg = check_outbound()
    results.append(("Outbound", ok, msg))

    ok, msg = get_public_ip()
    results.append(("PublicIP", ok, msg))

    vpn_flag = os.environ.get("VPN_ENABLED", "unset")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"## VPN Test — {now}\n")
        for name, ok, msg in results:
            f.write(f"- {name}: **{'PASS' if ok else 'FAIL'}** — {msg}\n")
        f.write(f"- ENV VPN_ENABLED: `{vpn_flag}`\n\n")

    print(f"✅ Logged -> {LOG}")

if __name__ == "__main__":
    main()
