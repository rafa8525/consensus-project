#!/usr/bin/env python3
"""Legacy fitness ingestion entrypoint: fail closed.

Do not produce fabricated Pixel Watch, COROS, or other health measurements.
An authenticated ingestion adapter must explicitly verify provider, timestamp,
schema and source provenance before writing to private runtime storage.
"""
from __future__ import annotations

import sys

def ingest() -> int:
    print(
        "BLOCKED: legacy fitness_ingest.py generated fabricated test measurements. "
        "No records written; configure an authorized Pixel Watch source.",
        file=sys.stderr,
    )
    return 2

if __name__ == "__main__":
    raise SystemExit(ingest())
