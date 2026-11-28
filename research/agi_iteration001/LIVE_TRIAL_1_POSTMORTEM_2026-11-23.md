# Live API trial #1 — postmortem and safe diagnostics repair (2026-11-23)

## Evidence recorded before the repair

- Protected GitHub workflow: https://github.com/rafa8525/consensus-project/actions/runs/45242358910
- Job: 137930074757, **failed** at `Execute exactly one protected Responses request` after immutable code fetch succeeded.
- The failed runner emitted only `Live trial stopped; inspect secure account usage and logs`, which intentionally hid raw API content and also prevented root-cause diagnosis.
- User's OpenAI Platform analytics screenshot for November 17–23 shows **one request, 643 tokens, $0.00021 spent** in AGI Research Sandbox. This establishes that the project processed and billed a request, but does not prove valid completed structured output.
- OpenAI's API Errors analytics page displayed **data unavailable**, not evidence of zero errors.
- User's screenshots show the one-shot API key was **revoked** and the GitHub `agi-research-live` environment has **no secrets**, with `OPENAI_PROJECT_ID` retained.
- Original first-request authorization must be treated as consumed. Never rerun GitHub Actions run #45242358910; its workflow checks first run attempt but billing cannot be undone.
- We do **not know** the actual post-HTTP error classification from the failed request. A likely explanation is an incomplete or invalid generated proposal, but that remains a hypothesis and must not be presented as confirmed.

## Offline repair

- Added `safe_trial_diagnostics.py`, returning only enumerated, non-secret failure codes for HTTP 4xx/5xx, network timeout, network failure, incomplete/refused model output, missing response text, invalid JSON, rejected proposal schema, local guard and unknown failure.
- Updated `one_shot_proposal_trial.py` to print a restricted structured error record and exit nonzero; it never prints HTTP response bodies, raw model responses, exception messages, request IDs, or secrets. The record says `request_may_have_been_billed: true` if the run reached the catch path and cannot independently establish actual spend.
- Added `test_safe_trial_diagnostics.py`, including fake secrets, HTTP classification, malformed responses, failure non-retry, sanitized CLI output. Test suite and CI remain offline.
- Successful research verification: https://github.com/rafa8525/consensus-project/actions/runs/45249406308, **302/302 tests**, commit `fc29e1d73a330fef8036923502f60e4528994cb1`. Registry: 55 proposed roles, zero production-enabled.

## IMPORTANT — Current live workflow still uses older pinned code

The installed `.github/workflows/agi-one-shot-live.yml` on **main** and research branch pins immutable source commit `10d829304ec11f4d036d8c882c2f24047f1922ad`. It therefore does **not** use these diagnostics! Changing only the branch Python file does not change what the live workflow runs.

Do **not** patch the pinned SHA or workflow in `main`, upload any new secret, or run a new API call as part of this offline repair. A subsequent live research request would require:
1. Explicit user authorization for a **second** paid request, separate from the consumed first-run authorization.
2. Fresh, project-scoped one-use key, confirmed rate limits and remaining $1 project headroom, verified model access.
3. A reviewed immutable code revision containing this repair, security verification, and separate user approval for changing **main** workflow metadata if required.
4. Exact environment branch check, manual GitHub reviewer gate, no retries and immediate key revocation afterwards.
5. Check usage and errors after run; never automatically retry on failed or uncertain results.

## Scientific interpretation

A billed single model call is real API integration evidence, not autonomous AI research, algorithm invention or recursive self-improvement. No validated live model proposal has been recorded and no production research agents were activated. This repair improves visibility of future failures and has zero experimental cost.
