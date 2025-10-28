#!/usr/bin/env python3
# test_twilio_guard.py
# Purpose: Run safe simulations of Twilio Guard rules without spamming real SMS.
# Outcome: Writes results to console and memory/logs/system/twilio_guard_test.md

import os
import datetime
from pathlib import Path
from twilio_guard import send_sms

# ===== CONFIG =====
LOG_DIR = Path("/home/rafa1215/consensus-project/memory/logs/system")
LOG_FILE = LOG_DIR / "twilio_guard_test.md"
TO = os.getenv("SMS_TO_NUMBER", "+16502283267")

def log(line: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")
    print(f"{ts} {line}")

def run_case(name, **kwargs):
    log(f"=== {name} ===")
    result = send_sms(to=TO, body=f"Test case: {name}", **kwargs)
    log(f"Result: {result}")
    log("")

def main():
    log("# Twilio Guard Test Run")
    # Case 1: Normal success path
    run_case("Success - Normal")

    # Case 2: Disabled globally
    os.environ["SMS_ENABLED"] = "false"
    run_case("Blocked - SMS disabled")
    os.environ["SMS_ENABLED"] = "true"

    # Case 3: Number not in whitelist
    os.environ["SMS_WHITELIST"] = "+19999999999"
    run_case("Blocked - Not whitelisted")
    os.environ["SMS_WHITELIST"] = TO

    # Case 4: Quiet hours
    os.environ["SMS_QUIET_HOURS"] = "00-23"  # block all hours
    run_case("Blocked - Quiet hours")
    os.environ["SMS_QUIET_HOURS"] = "21-08"

    # Case 5: Rate limit exceeded
    os.environ["SMS_MAX_PER_HOUR"] = "0"
    run_case("Blocked - Rate limit")
    os.environ["SMS_MAX_PER_HOUR"] = "1"

    log("=== Test suite complete ===")

if __name__ == "__main__":
    main()
