"""Inert until a *separately approved* second live API research trial.

No API calls without --live, protected environment, and explicit approval.
The former one-shot key is revoked and must never be reused. This script is
not referenced by the installed workflow on main or the research branch.
"""
from __future__ import annotations
import argparse
import json
import os
from one_shot_proposal_trial import (
    OnceHTTPClient, dry_run, live_once, verify_manual_context)
from safe_trial_diagnostics import safe_failure_record

TRIAL2_OUTPUT_TOKENS=1600

def main():
    p=argparse.ArgumentParser()
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run",action="store_true")
    modes.add_argument("--live",action="store_true")
    args=p.parse_args()
    if args.dry_run:
        receipt=dry_run()
        receipt["trial"]="TRIAL2_PREPARATION_ONLY"
        print(json.dumps(receipt,sort_keys=True))
        return
    # A dedicated manual GitHub job must set this exact unique trial2 intent.
    if os.environ.get("AGI_TRIAL2_EXPLICIT_APPROVAL")!="YES-TRIAL-2":
        raise SystemExit("BLOCKED: trial2 approval marker missing")
    transport=None
    try:
        # Validate context before constructing an HTTP transport. This ensures
        # rejected workflow/key settings cannot be reported as billed requests.
        verify_manual_context(os.environ)
        transport=OnceHTTPClient(
            os.environ["OPENAI_API_KEY"],os.environ["OPENAI_PROJECT_ID"],
            output_token_cap=TRIAL2_OUTPUT_TOKENS)
        receipt=live_once(os.environ,transport=transport,
                          output_token_cap=TRIAL2_OUTPUT_TOKENS)
        receipt["trial"]="TRIAL2"
    except Exception as exc:
        attempted=transport is not None and transport.calls>0
        print(json.dumps(safe_failure_record(exc,attempted_request=attempted),sort_keys=True))
        raise SystemExit(1) from None
    print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
