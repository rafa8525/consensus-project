#!/usr/bin/env python3
"""Fail closed until a validated security audit is integrated."""
import sys

def main():
    print(
        "ERROR: Verified security-audit runner is not yet "
        "configured. No audit has been performed.",
        file=sys.stderr,
    )
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
