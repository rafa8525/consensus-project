# Hive Mind — Merged Recommendations

## [1] Finish queue_worker.py

**From:** Example Agent

**Key:** `d28610e2c1`

Complete at-most-once job claim + done/ finalization with try/finally.

## [1] Guard SMS by default

**From:** Example Agent

**Key:** `7734ee2d09`

Ensure SMS_ENABLED=false and whitelist only.

## [1] Guard: stop on rc=0

**From:** Reliability Ranger

**Key:** `9040949745`

Break loop when rc==0 to avoid thrash.

## [2] Lock cleanup

**From:** Reliability Ranger

**Key:** `0fbb8109e6`

Ensure SIGTERM handler removes lockfile; verify at start.
