# Experiment #2 failure analysis and offline schema-contract repair
Date: 2026-11-24 Pacific. **Research-only; no live API request authorized or performed by these repairs.**

## Observed failure, not conjecture
- Original paid experiment #2: https://github.com/rafa8525/consensus-project/actions/runs/45493656099, job 138798320836.
- Pinned source retrieval succeeded. Single guarded OpenAI Responses API execution step failed with exit code 1.
- Allowlisted receipt: `failure_category=PROPOSAL_VALIDATION_FAILED`, `response_status=completed`, `output_text_present=true`, `reasoning_tokens=0`, `input_tokens=275`, `output_tokens=191`, `request_may_have_been_billed=true`, `automatic_retry_permitted=false`.
- This was **not output-token exhaustion**. The error indicates rejection by the application validation pipeline after a completed model response.
- Since the raw response was intentionally not persisted, **the specific invalid proposal field is UNKNOWN** and cannot be recovered from this job log.
- Check actual Experiment #2 charge in OpenAI Platform. Do not re-run job or dispatch another request without new explicit authorization.

## Code defects found and repaired on research branch
1. Structured Output schema previously allowed arbitrary dataset names, budget integers, model values and stop-condition strings while offline validator accepted only fixed values in a fixed order.
2. Tightened supported strict-schema enum options for `dataset_ids`, `compute_budget`, model `kind`, `n`, `alpha`, and `stop_conditions`. Remaining ordering and creative text constraints stay enforced by a separate validator, because schema does not fully express semantic constraints in its supported subset.
3. Tightened prompt instructions on field order, experiment ID and plain-text hypothesis/falsifier requirements, while preserving useful research text generation.
4. Added `ProposalValidationError` with closed-set reason identifiers: RESPONSE_SHAPE, EXPERIMENT_ID, HYPOTHESIS_TEXT, FALSIFIER_TEXT, METRIC_MISMATCH, DATASET_MISMATCH, BUDGET_MISMATCH, STOP_CONDITION_MISMATCH and CANDIDATE_MISMATCH.
5. Existing validator still rejects unapproved datasets, candidates, resource budgets and unsafe instructions; no relaxation of production limits, model execution, data access or additional HTTP calls.
6. Added a guard for credential-like strings in generated hypothesis/falsifier text after an integration regression test caught an allowed-looking `sk-` token.
7. Sanitized failure receipts can now include a **fixed validation_reason** rather than arbitrary generated text. All model text and credentials remain excluded from logs.

## Verified testing
- Final offline CI: https://github.com/rafa8525/consensus-project/actions/runs/45496037001.
- **358 of 358 tests passed** at research commit `78c884ca856c78cfa731dc21111a36a86cdad66b`, including simulated completed-but-rejected API envelopes, exact one-call mock counting, safe metadata, secret redaction, schema constraints and manual-only review-candidate tests.
- Candidate `research/agi_iteration001/TRIAL2_SCHEMA_REPAIR_WORKFLOW_REVIEW_20261124.yml` is NOT under `.github/workflows`; it is inert and pinned to **`3957ef772fabb8d1c72bccc1b070869eb4ac9174`**, the tested research commit containing the implementation and integrated regression tests.
- Both installed `.github/workflows/agi-trial2-live.yml` files remain pinned to previous `f5ff59ce7332ff0fd3da69f7ded9349b6b5aeef9`. They were not modified in this repair.

## Known limits and next approval boundaries
- Passing offline tests does not prove the next live API result will pass. Root cause field of run #2 remains unknown; further semantic restrictions may be discovered by a future specifically approved request.
- The prior single billable request was used. Any next experiment needs new separate explicit spending authorization, fresh budget review, and a new approval at the protected GitHub environment.
- Installing the repaired candidate on BOTH main and research branches would change the executable workflow pin and requires a new explicit user approval.
- No keys, credits, production services, or live agent operations changed here; registry still reports 55 declared roles and zero production-enabled.
