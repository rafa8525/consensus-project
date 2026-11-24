# AGI Trial #2 — isolated repair review (2026-11-24)

## Scope and non-execution statement
The user asked to proceed with repairs after reviewing 12 public technical documentation/support sources. All edits in this round affect **only** `research/agi-iteration-001-20261119` and its already-existing, automatically triggered **offline research-verification CI**. No API secret was re-created, no live trial dispatched, and no production services modified. CI makes no paid model API calls.

## Findings and fixes
1. **Charge attribution failure:** the previous `trial2_proposal_trial.py` catch path always set `request_may_have_been_billed=true`, even if environment/credential verification failed *before a network attempt*. Repaired by validating workflow context first, constructing an instrumented `OnceHTTPClient`, and basing the field on `transport.calls > 0`. This flag still means *possibly billed*, never *verified billed*. Real costs must be checked on OpenAI Platform.
2. **Malformed response output:** `one_shot_proposal_trial.py` assumed `output`, `message.content`, and each output item were well-formed lists/dictionaries. Repaired by checking types and raising safe fixed ValueErrors; raw response text is never logged.
3. **Verification:** added mock tests for malformed output, invalid content shapes, no automatic retry, preflight failure vs attempted call, safe status classification and secret redaction.
4. **Reviewable immutable workflow candidate:** `TRIAL2_REPAIRED_WORKFLOW_REVIEW_20261124.yml` is outside `.github/workflows`, pinned to the first 326-test successful repair commit `a4b2bb28cae310a270afcb0716fb09a0fff77ade`. It is **not installed**. A static test checks manual trigger, bounded permissions, restricted branch, GitHub review environment and exact single trial2 command. It corrects an earlier misleading comment implying the old installed workflow is inert.

## Reference and change boundary
- Initial repaired offline CI: https://github.com/rafa8525/consensus-project/actions/runs/45442465997 — **326/326 tests passed**.
- Original installed experiment 2 workflow still pinned to `25f362ed74f3227e44df815eb376b70791cb4a85`, on both `main` and research branch. That executable file has NOT been changed in this repair.
- The repaired workflow candidate is pinned to `a4b2bb28cae310a270afcb0716fb09a0fff77ade`, a commit containing repairs and offline tests. Newer research-only tests/docs do not alter code at that pinned revision.

## Open questions before any second paid model call
- Live model access, supported JSON schema keywords, reasoning/output token budget and pricing still require up-to-date independent verification.
- Output-token exhaustion is plausible but **not proven** as the first experiment's root cause.
- A SHA-256 hash alone does not preserve enough scientific evidence to evaluate proposal quality. Design a secure non-secret evidence and review protocol before concluding research success.
- The project has 55 **defined** roles but zero independently confirmed production-enabled AGI research workers. This repair does not activate any of them.

## Gate for next operation
Changing `.github/workflows/agi-trial2-live.yml` on `main` and the research branch to refer to the repaired code requires a **separate explicit approval**. Creating an API key, funding, or making a paid API request would require additional explicit authorization. No automatic retry or production change may be inferred from this repair.
