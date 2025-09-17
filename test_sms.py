#!/usr/bin/env python3
"""
test_sms.py
Safe tester for twilio_guard.py

- Sends 3 test messages to verify daily limits
- Tries a duplicate message (should be blocked)
- Prints results clearly to console
"""

import datetime
from pathlib import Path
import importlib.util
import sys

PROJECT_ROOT = Path("/home/rafa1215/consensus-project").resolve()
GUARD_FILE = PROJECT_ROOT / "twilio_guard.py"

# Dynamically load twilio_guard.py
spec = importlib.util.spec_from_file_location("twilio_guard", str(GUARD_FILE))
twilio_guard = importlib.util.module_from_spec(spec)
sys.modules["twilio_guard"] = twilio_guard
spec.loader.exec_module(twilio_guard)

TO_NUMBER = "+16502283267"

def run_tests():
    now = datetime.datetime.now()
    print(f"[{now.isoformat()}] Starting SMS guard tests\n")

    # 1. Send first message
    res1 = twilio_guard.send_sms(TO_NUMBER, "Test 1: First message")
    print("Test 1:", res1)

    # 2. Send duplicate immediately (should be blocked as duplicate)
    res2 = twilio_guard.send_sms(TO_NUMBER, "Test 1: First message")
    print("Test 2 (duplicate):", res2)

    # 3. Send two more distinct messages (to hit daily limit)
    res3 = twilio_guard.send_sms(TO_NUMBER, "Test 2: Second message")
    print("Test 3:", res3)

    res4 = twilio_guard.send_sms(TO_NUMBER, "Test 3: Third message")
    print("Test 4:", res4)

    # 4. Try a 4th message (should be blocked by daily limit)
    res5 = twilio_guard.send_sms(TO_NUMBER, "Test 4: Over daily limit")
    print("Test 5 (limit exceeded):", res5)

    print("\n✅ Done. Check memory/logs/system/twilio_guard.log for details.")

if __name__ == "__main__":
    run_tests()
