# Experiment 2 — compatibility, diagnostics, and evidence approval review
Date: 2026-11-24 (Pacific). Status: **OFFLINE ONLY; NOT INSTALLED.**

## Why this exists
The first live request was billed ($0.00021, 643 tokens in the user's Platform screenshot) but the workflow did not validate a proposal. Its exact failure cannot be proven retrospectively. Experiment 2 had a secure, corrected one-shot workflow, but used the default `medium` reasoning setting, with a 1,600-total-output-token limit. This can lead to an incomplete response if hidden reasoning consumes the allowance.

## Independent documentation check
- Official model documentation: https://developers.openai.com/api/docs/models/gpt-6-luna — `gpt-6-luna` supports `reasoning.effort: none` and Structured Outputs.
- Reasoning token accounting: https://developers.openai.com/api/docs/guides/reasoning — hidden reasoning tokens count against `max_output_tokens`; default Luna effort is `medium`.
- Structured schema guidance: https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses — strict JSON Schema support, matching `text.format`, `additionalProperties:false`, and required keys.
- Actual live compatibility and output success remain **unverified**, because no new paid request was authorized.

## Bounded changes prepared on research branch
1. `openai_proposal_adapter.py`: optional `reasoning_effort` allowing only `none` or the previously unchanged default; trial2 chooses `none`, and trial1's default remains unchanged.
2. `one_shot_proposal_trial.py`: validates optional `reasoning:{"effort":"none"}` in the HTTP body, refuses any other reasoning shape/setting, retains exact model and output budget, no tools, no storage and no retries.
3. `trial2_proposal_trial.py`: passes `reasoning_effort="none"` to the existing bounded 1,600-token request, and retains protection markers, one-attempt and preflight charge diagnosis.
4. `proposal_evidence.py`: produces a deterministic, safe research receipt **only after** a fully validated proposal, including proposal/hypothesis/falsifier SHA256 hashes, fixed candidate specs, dataset IDs, metric, local compute budget, and explicit `experiment_executed=false`, `measured_improvement=false` and `promotion_approved=false`. Never prints raw model prose, credentials, response ID, or untrusted strings. A digest is **not** independent proof of research quality; any later qualitative review needs a separate private, approved capture process.
5. New mock tests verify a single exact reasoning-none request, rejection of unapproved effort, no change to trial1, safe receipt output and absence of false promotion claims.
6. GitHub offline verification https://github.com/rafa8525/consensus-project/actions/runs/45466273695: **343/343 tests passed**, run head commit `a69e1bfe606226df8bc40fefec0ede1f847a6318`. The review candidate is pinned to immutable tested code commit `b2ad3746297e003b030889ccdb8970284f8e6a47`, containing the implementation and initial 339 passing tests.

## Exact workflow proposed, not installed
`research/agi_iteration001/TRIAL2_COMPATIBILITY_REVIEW_20261124.yml`
The existing installed file remains `.github/workflows/agi-trial2-live.yml` on `main` and `research/agi-iteration-001-20261119`, pointing to older `a4b2bb28cae310a270afcb0716fb09a0fff77ade`.

Proposed future metadata-only change: replace exactly that file on both branches using the reviewed candidate; preserve manual-only `workflow_dispatch`, strict research-branch check, `YES-TRIAL-2` typed confirmation, `agi-research-live` environment, required human review, `contents:read`, single pinned code checkout, and one live command. No other code or service changes.

## Hard approval boundaries
- Updating the installed workflow on `main` and research branch requires a new **explicit authorization**.
- Creating a new API key or GitHub secret requires independent authorization and user-controlled credential handling.
- Making **one additional potentially billed API call** requires a **separate explicit authorization** and fresh verification of project limit, model permissions, and security controls.
- Do not retry failed or uncertain live calls automatically, do not activate any 55 production agent roles, and do not change production systems.
