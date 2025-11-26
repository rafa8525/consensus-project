#!/usr/bin/env python3
"""
vpn_functional_test_runner.py

Generates a functional test report for the automatic VPN activation feature.
The script documents test cases and marks their result as "SIMULATION_ONLY"
with manual verification required. Intended to be run whenever you want a
fresh functional test report.

Output:
- memory/logs/system/vpn_test_report_YYYY-MM-DD_HHMMSS.md
- memory/logs/system/vpn_test_report_latest.md
"""

import datetime
from datetime import timezone
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "memory" / "logs" / "system"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(timezone.utc)


def build_test_cases() -> List[Dict[str, str]]:
    """
    Define the functional VPN test cases.
    These are conceptual and assume manual / external verification for now.
    """
    return [
        {
            "id": "VPN-FUNC-001",
            "scenario": "Connect on BART public Wi-Fi (SSID BART-WiFi)",
            "expected": "VPN auto-activates within N seconds and all traffic is routed through VPN; log entry written.",
        },
        {
            "id": "VPN-FUNC-002",
            "scenario": "Connect on Muni public Wi-Fi (SSID MuniFreeWiFi)",
            "expected": "VPN auto-activates within N seconds and all traffic is routed through VPN; log entry written.",
        },
        {
            "id": "VPN-FUNC-003",
            "scenario": "Connect on generic open public Wi-Fi (e.g., coffee shop)",
            "expected": "VPN auto-activates when unsecured/open network is detected; log entry written.",
        },
        {
            "id": "VPN-FUNC-004",
            "scenario": "Connect to home Wi-Fi (known trusted SSID)",
            "expected": "VPN remains OFF or follows home profile rules; no forced auto-activation; logs reflect correct behavior.",
        },
        {
            "id": "VPN-FUNC-005",
            "scenario": "Switch from home Wi-Fi to public Wi-Fi",
            "expected": "VPN transitions from OFF (home) to ON (public) quickly; no traffic leakage; logs show transition.",
        },
        {
            "id": "VPN-FUNC-006",
            "scenario": "Disconnect from public Wi-Fi (no network)",
            "expected": "VPN disconnects gracefully; no phantom connection; logs show clean teardown.",
        },
        {
            "id": "VPN-FUNC-007",
            "scenario": "Logging and error handling",
            "expected": "All auto-connect attempts are logged; failures have error details; no silent failures.",
        },
    ]


def generate_report_content() -> str:
    now = utc_now()
    ts_str = now.isoformat()
    date_str = now.date().isoformat()

    tests = build_test_cases()

    lines: List[str] = []
    lines.append("# VPN Functional Test Report")
    lines.append(f"- Generated (UTC): {ts_str}")
    lines.append(f"- Date: {date_str}")
    lines.append("")
    lines.append("## Overview")
    lines.append(
        "This report documents functional test cases for the automatic VPN "
        "activation feature. Current results are based on **simulation only**; "
        "manual verification is still required on real networks/devices."
    )
    lines.append("")
    lines.append("## Test Cases")
    lines.append("")

    for t in tests:
        lines.append(f"### {t['id']}: {t['scenario']}")
        lines.append(f"- **Expected behavior:** {t['expected']}")
        lines.append("- **Auto result:** SIMULATION_ONLY (no live VPN checks performed)")
        lines.append("- **Manual verification required:** YES")
        lines.append("- **Manual notes:** _(fill in after on-device test)_")
        lines.append("")

    lines.append("## Summary")
    lines.append(
        "- All test cases are defined and documented.\n"
        "- Automation is currently **log/simulation only**; no live VPN CLI integration in this script.\n"
        "- Use this report as a checklist when manually testing on actual devices and networks."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    now = utc_now()
    stamp = now.strftime("%Y-%m-%d_%H%M%S")
    report_path = LOG_DIR / f"vpn_test_report_{stamp}.md"
    latest_path = LOG_DIR / "vpn_test_report_latest.md"

    content = generate_report_content()
    report_path.write_text(content, encoding="utf-8")
    latest_path.write_text(content, encoding="utf-8")

    print(f"VPN functional test report written to: {report_path}")
    print(f"Latest report also available at: {latest_path}")


if __name__ == "__main__":
    main()
