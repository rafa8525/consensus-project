#!/usr/bin/env python3
"""ACS-03 cloud daily job. Deploy privately; do not run from GitHub worktree.

Runs import, guarded idempotent publish and real source freshness checks.
Failure exits nonzero. Never logs health totals, OAuth tokens or raw records.
"""
from __future__ import annotations
import resource
import sys
from health_connect_memory_import import import_candidate
from health_connect_daily_publish import publish
from health_connect_freshness import verify

LIMIT=2*1024**3

def main():
    try:
        soft,hard=resource.getrlimit(resource.RLIMIT_AS)
        ceiling=min(LIMIT,hard) if hard!=resource.RLIM_INFINITY else LIMIT
        resource.setrlimit(resource.RLIMIT_AS,(ceiling,hard))
        candidate=import_candidate()
        result=publish(candidate)
        passed,reason=verify()
        if not passed:
            print("ACS03_CLOUD_CYCLE=FAIL VERIFY_"+reason,file=sys.stderr)
            return 2
        print("ACS03_CLOUD_CYCLE=PASS")
        print("SOURCE=HEALTH_CONNECT_FITBIT")
        print("PACIFIC_DATE="+result["local_date"])
        print("VERIFIED_RECORDS="+str(result["records"]))
        print("COMPLETE_DAY_COVERAGE=UNVERIFIED")
        return 0
    except Exception as exc:
        print("ACS03_CLOUD_CYCLE=FAIL "+type(exc).__name__,file=sys.stderr)
        return 2
if __name__=="__main__":
    raise SystemExit(main())
