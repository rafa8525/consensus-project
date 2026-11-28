# Experiment 2 safe receipt upgrade — review only

Updated 2026-11-24. This is **not** authorization to run a paid API call, configure a key, or replace the installed workflow.

## Verified status
- Offline GitHub CI: https://github.com/rafa8525/consensus-project/actions/runs/45471458136 — **347/347 tests** passed at commit `f5ff59ce7332ff0fd3da69f7ded9349b6b5aeef9`.
- Installed `.github/workflows/agi-trial2-live.yml` is still pinned to `b2ad3746297e003b030889ccdb8970284f8e6a47` on both branches.
- Proposed replacement `research/agi_iteration001/TRIAL2_DIAGNOSTICS_REVIEW_20261124.yml` lives outside the executable GitHub Actions directory and pins `f5ff59ce7332ff0fd3da69f7ded9349b6b5aeef9`.
- No new API calls, keys, credit spending, agent activations, or production-service changes.

## Repair rationale
1. Existing code safely extracted `response_status`, `incomplete_reason`, boolean text/refusal presence, and bounded `input_tokens`, `output_tokens`, `reasoning_tokens`, but live error receipts only included `failure_category`.
2. `OnceHTTPClient.last_metadata` now holds the sanitized envelope after a response, before any later parser/validator failure.
3. `trial2_proposal_trial.py` includes safe metadata on failure **only when available**, preserving the request-attempt billing-uncertainty field and no-retry rule.
4. The error receipt ignores arbitrary dictionaries and never outputs the raw response, request ID, API credential, or model text.
5. Tests simulate exhausted output budgets, weird statuses, malformed token fields, secret strings and network-attempt counts without external API requests.

## Scientific limits
- The root cause of the first paid attempt remains unknown.
- A request with `reasoning.effort: none` and 1600 max output tokens is documented as allowed, but live success is not verified.
- The research receipt identifies the fixed baseline and candidate model catalog; it does not prove independent AI innovation or training improvements.
- Operational status of the 55 independent agents remains unverified.

## Next approval gate
Replacing the installed manual workflow on both branches with the reviewed candidate would modify which research commit a future explicitly approved action runs. Require explicit user authorization before changing either installed workflow.
A second potentially billable API request and any new credential require their own separate authorization.
