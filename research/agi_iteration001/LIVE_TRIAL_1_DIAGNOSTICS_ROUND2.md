# Live AGI trial — offline diagnosis round 2 (2026-11-23)

## Findings
OpenAI's documented Responses API behavior says `max_output_tokens` includes visible text **and reasoning tokens**. A model response that reaches the limit can finish with `status=incomplete` and `incomplete_details.reason=max_output_tokens`.
- https://developers.openai.com/api/docs/guides/reasoning?api-mode=responses
- https://developers.openai.com/api/reference/resources/responses/methods/create

The first live attempt (https://github.com/rafa8525/consensus-project/actions/runs/45242358910) generated **one billed API request**; the user's OpenAI analytics showed 643 total tokens and $0.00021 charged. The runner suppressed response details. Therefore it is **not proven** that output-token exhaustion, invalid JSON, request rejection, or another failure actually occurred.

## Changes implemented only on the isolated research branch
- `response_envelope_diagnostics.py`: inspect only enumerated API status, a safe subset of incomplete reasons, presence of text/refusal, and bounded usage counts; never return raw text, response IDs or keys.
- `one_shot_proposal_trial.py`: attach sanitized response metadata to local transport results for classification; not outputting metadata or response body to logs.
- `openai_proposal_adapter.py`: raises a fixed internal error when a response was incomplete specifically due to the max output limit.
- `safe_trial_diagnostics.py`: maps the new condition to `OUTPUT_TOKEN_BUDGET_EXHAUSTED` without raw exception messages.
- `test_response_envelope_diagnostics.py`, updated test cases: complete, incomplete, missing text, refusal, unknown values, safe-count validation, no sensitive leakage, one-call/no-retry rule.
- GitHub Actions run: https://github.com/rafa8525/consensus-project/actions/runs/45250308972 ; commit `3174eb19a6b066c86f3823bf94584cea395d725c`; **312/312 tests pass**, 55 proposed roles and zero production-enabled.

## Stop conditions
**Do not run or retry the live workflow**. The old immutable SHA in `.github/workflows/agi-one-shot-live.yml` is still `10d829304ec11f4d036d8c882c2f24047f1922ad` and will not use the repaired code. The one-shot API key has been revoked and removed from the GitHub environment. The first user's paid API request authorization was consumed.

For any future experiment, obtain separate explicit approval for: (1) the new paid API request, (2) a new scoped single-use key, and (3) changing the main-branch workflow's immutable code pin. Verify project billing and model restrictions freshly. A new workflow run has a separate approval gate but GitHub is not a global one-request guarantee.

## Research significance
This fixes failure observability for a hypothetical second request; it does not demonstrate algorithm invention or AGI. It does not activate any of 55 proposed agents or alter production.
