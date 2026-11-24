# Project AGI — canonical handoff and no-repeat record
**As of:** 2026-11-24, Pacific time  
**Repository:** `rafa8525/consensus-project`  
**Research branch:** `research/agi-iteration-001-20261119`  
**Record type:** Historical project handoff; non-executable documentation only.  
**Status:** The **third separately authorized live API request succeeded** in generating one schema- and application-validated research proposal. No training or promotion was performed.

> **Read this before modifying or rerunning anything.** Distinguish a successful API proposal from actual learning, training, or AGI. Historical repair notes contain stale "not installed" warnings; use the latest verified state and exact run IDs below.

## 1. Original mission — still in effect
Project AGI / AI Consensus follows Version 3 goals:
- Account for **all 55 existing agent roles**, eventually achieving real, observable coordination; a registry of 55 roles is **not** 55 currently running independent agents.
- From one high-level user objective, autonomously plan, delegate, execute permitted steps, test, recover from safe errors, and report verified outcomes with minimal manual copying.
- Design, train, evaluate, and recursively improve new AI models, with measurable comparisons and rejection of regressions; eventually add daily agent review, shared durable memory, proactive assistance and reporting.
- Reuse existing GitHub, PythonAnywhere, Google Cloud and connected context where appropriate. Do not assume those integrations have been certified merely because this API test passed.
- **Bounded approvals:** separate explicit permission for new API spending, credentials, workflow installation, destructive changes, production modifications, and activating autonomous agents. No Slack, no automatic retry of uncertain paid calls, no secret exposure. User favors one concise approval request per real boundary.

## 2. Historical progression and lessons
| Event | Evidence and result | Durable lesson |
|---|---|---|
| First live API attempt, Nov 23 | GitHub run [45242358910](https://github.com/rafa8525/consensus-project/actions/runs/45242358910); failed after pinned source fetch. Platform screenshot showed **1 request, 643 tokens, $0.00021**. Error details unavailable. | Do **not** claim output exhaustion was proven. First key was revoked and deleted from GitHub. Never rerun this job. |
| Diagnostics repairs, Nov 23 | GitHub runs [45249406308](https://github.com/rafa8525/consensus-project/actions/runs/45249406308): **302 tests**, and [45250308972](https://github.com/rafa8525/consensus-project/actions/runs/45250308972): **312 tests**. | Classify safe failures; capture allowlisted response status/usage, never raw secrets or response text. |
| Trial #2 offline preparation, Nov 23–24 | Manual gated workflow and bounded 1600-token request prepared, one attempt, no retries, no tools, `store=false`; [45251851821](https://github.com/rafa8525/consensus-project/actions/runs/45251851821): **323 tests**. | Separate research code, inert workflow candidates and reviewed installation from an actual authorized API request. |
| Further safety/compatibility repairs, Nov 24 | Offline progression: **326**, **330**, **339**, **343**, **347** passing tests. Added request-attempt billing uncertainty, malformed response guards, `reasoning.effort=none`, safe SHA-256 research evidence, sanitized token counts. | Keep immutable pinned code in sync with tested fixes only via a reviewed workflow change. |
| Second paid API attempt, Nov 24 | GitHub run [45493656099](https://github.com/rafa8525/consensus-project/actions/runs/45493656099), job 138798320836: **FAILURE** in proposal validation after a **completed** model response. Input **275** tokens, output **191**, reasoning **0**, text present. | **Not** an API availability or token-exhaustion failure. AI-facing schema was looser than application validator. Exact rejected field unknown because raw model output was not retained. **Never rerun** this job. |
| Schema and semantic validation repair, Nov 24 | Tightened schema enums for approved datasets/budgets/candidate parameters/stops; tightened prompt; added closed-set field error reasons and protection against key-like strings; final CI run [45496037001](https://github.com/rafa8525/consensus-project/actions/runs/45496037001): **358/358 tests passed**. | Preserve strict downstream semantic validation; do not weaken the guard to make a demo green. |
| Installed repaired code, Nov 24 | Executable workflow `.github/workflows/agi-trial2-live.yml` on `main` and research branch, **identical** contents, pins **`3957ef772fabb8d1c72bccc1b070869eb4ac9174`**; installation commits `e28a83ef9c9daf12df89f3697bba9809749def8b` (main), `15fb909c4732c49972f94991864642d5d3220b93` (research). | Pin is authoritative; edits to branch Python code do not affect already installed workflow unless pinned SHA changes. |
| Third separately authorized paid API request, Nov 24 | GitHub run [45499920454](https://github.com/rafa8525/consensus-project/actions/runs/45499920454), job **138820180508**, **SUCCESS**. Sanitized runner receipt: `status=ONE_PROPOSAL_RECEIVED`, `trial=TRIAL2` (legacy name), `external_calls=1`, model `gpt-6-luna`, `research_evidence.proposal_validated=true`, `origin=live_api`. | **Integration milestone reached.** Exactly one API-generated proposal passed both schema handling and strict local validation; prior paid authorization is **consumed**. |

**Naming pitfall:** GitHub workflow/CLI remain labeled *trial2*, but run **#1** of that workflow was the **second** paid experiment, and run **#2** was the **third** paid experiment. Never equate GitHub workflow name or run index with the overall experiment number.

## 3. Verified successful outcome
For [run 45499920454](https://github.com/rafa8525/consensus-project/actions/runs/45499920454):
- GitHub protected environment `agi-research-live` approved; pinned source checkout succeeded; one bounded API execution step succeeded.
- Sanitized receipt: `status=ONE_PROPOSAL_RECEIVED`, `external_calls=1`, `proposal_validated=true`.
- Proposal SHA-256: `810e978f7ec87d6e25a327fc2d1e8f84fa125f20f899ad4b765d7f45f4102489`.
- Approved research candidates: `word_nb` baseline; `word_char_nb` with `n=3, alpha=0.5`; `word_char_nb` with `n=4, alpha=1.0`.
- Dataset IDs: `train-v1` and `validation-v1`. Evaluation metric: `validation_macro_f1`. Experimental budget: **3 fits, 30 examples**.
- Important receipt flags: `experiment_executed=false`, `measured_improvement=false`, `promotion_approved=false`, `production_changes=false`.
- **Actual charge for third attempt NOT VERIFIED** by the script; check OpenAI Platform. A successful request does not prove model-training success or science advancement. Raw proposal text was deliberately not retained in public CI logs, so its prose cannot be reconstructed from the hashes alone.

## 4. Safety controls and previously checked finances
- Executable workflow: `.github/workflows/agi-trial2-live.yml`; manual `workflow_dispatch` only; exact confirmation `YES-TRIAL-2`; only on `research/agi-iteration-001-20261119`; `github.run_attempt==1`; pinned SHA verification; `permissions: contents: read`; GitHub environment `agi-research-live` requires human reviewer; no automatic retries or production changes.
- Runner reads the project-scoped credential via `secrets.OPENAI_API_KEY` and project ID via `vars.OPENAI_PROJECT_ID`, never from source code. User created new key and confirmed environment secret installed. Do not expose keys, and do not assume key is still active or still needed.
- User's screenshots **before the third attempt** showed **$1 enforced project spend limit**, **$0.00 displayed project spend**, **$10.00 organization API credit balance**, **auto-reload OFF**, and `gpt-6-luna` on project allowlist. These are historical checks, **not current balance or actual post-experiment charges**.
- New paid request is **not authorized**. Authorization for run 45499920454 was specifically one additional request; it was used. Do not invoke Run workflow or Re-run jobs to verify anything.
- Preserve approvals for workflow edits, new keys, new spending, destructive/production steps, and agent activation. Only user can grant next authorization.

## 5. Do not repeat
1. **Do not repeat Experiment #1 or #2,** or start another live workflow to prove what #3 has already demonstrated.
2. **Do not rediagnose token exhaustion as the confirmed cause of Experiment #1**; it remains unknown.
3. **Do not claim #2 failed because of the API**; it returned `completed`, with text, and failed downstream local validation.
4. **Do not rerun paid failures** or use GitHub's `Re-run jobs` controls.
5. **Do not make the same schema and validator mismatch**: constraints of model-generated fields must be aligned with strict application-level validators; preserve safe field-specific reason codes.
6. **Do not install new workflows just to keep testing successfully completed integration.** Any changed immutable pin requires a new approved review candidate.
7. **Do not confuse the registry of 55 roles with 55 operational agents.** Past tests reported 55 defined roles but **zero production-enabled**.
8. **Do not equate proposal generation with training/evaluating new models.** Evidence currently proves a validated *proposal*, not improved model accuracy.
9. **Do not persist secrets or raw model text in public GitHub logs, Notion, docs, or chat**. Scientific review of full prose needs a separate approved private protocol.
10. **Do not repeatedly ask the user for already-known facts.** Read this record, consult fresh execution results, and raise only a genuine approval or missing-dependency question.

## 6. Next phase, not yet authorized or completed
**Recommended next work: research proposal evaluation and measured model improvement, offline first.**
1. Freeze the successful API integration as a documented milestone; protect the current functional pin and regression suite.
2. Build a **fully offline** evaluator that uses an allowed, reviewed proposal or a fixed synthetic fixture; establish repeatable baselines, holdout rules, seeded experiments and a metric report. Do **not** pretend public SHA hashes reveal the original proposal prose.
3. Distinguish three separate milestones: (a) proposal accepted (DONE), (b) models actually evaluated against pre-agreed datasets and metrics (NOT YET CERTIFIED), (c) improvements verified and safely reviewed for promotion (NOT DONE).
4. Inventory and account for all 55 roles, with an explicit role-to-execution map; only claim actual agent collaboration when there is independently inspectable evidence.
5. Design safe, rollbackable self-improvement with comparisons and approval gates; retain durable lessons and prevent regressions.
6. Before any **new API request**, verify post-attempt spend, account credit balance, currently enforced $1 project cap, API key scope, model allowance, environment reviewer rules, exact code pin and single-call budget; obtain a new explicit spending approval.
7. **Nonblocking documentation cleanup:** installed executable workflow's leading comments inaccurately call it an inert review-only candidate. Do not silently edit the live workflow; propose a separate reviewed cosmetic fix if/when modifying it for another legitimate reason.

## 7. Resume instructions — minimum prompt
> Resume `rafa8525/consensus-project` Project AGI from `research/agi_iteration001/AGI_PROJECT_HANDOFF_AND_NO_REPEAT_20261124.md`. The third live API experiment already **succeeded** (run 45499920454, one validated proposal, no training). **Do not rerun** any paid workflow or rework the solved API/schema integration. Continue only with the next offline, measurable model-evaluation milestone using all 55 role definitions in planning, while respecting explicit user approval for any new spend, credentials, workflow/prod changes or agent activation. Confirm fresh evidence before claiming success.

## 8. Follow-up progress — bounded offline model evaluation (Nov 24, 2026)
- **This phase is no longer merely planned.** Added `bounded_proposal_evaluation.py` and `test_bounded_proposal_evaluation.py` on the isolated research branch; the offline verification workflow now runs both. **No executable live workflow on main was changed.**
- Verified research CI: https://github.com/rafa8525/consensus-project/actions/runs/45501425963 — **365 of 365 tests passed** at commit `93ac7f5b9514c697c16ec23961d1643a1c51ccb1`; full workflow including independent CI checks completed successfully.
- The evaluator uses the already approved **fixed offline proposal fixture**, not the unretained prose from the successful third API call. It fits **exactly three classifiers**, using 18 hand-authored training examples and 12 disjoint hand-authored validation examples; no holdout data accessed; no API calls; no production promotion.
- Measured internal validation `macro-F1`: word NB **0.481818** (6/12 correctly classified); word+3gram alpha=0.5 **0.742857** (9/12); word+4gram alpha=1.0 **0.742857** (9/12). Validation tie-break favors candidate index 1 (3gram, alpha 0.5); gain over baseline is **0.261039**. These are *internal validation results only*, not external or independent generalization.
- Results are deterministic against dataset SHA256 `4e75caf2d8e098cd64243b9ff1619455afa74670efb180b8f72804ed5a2be7cd` and include fixed fit cap, no holdout, zero external calls, no production changes and no authorization to promote.
- **Do not repeat this three-fit comparison simply to prove it works.** Next assess external validity, dataset provenance, non-regression and independently reviewed improvement gates. Existing `replicated_model_evaluation.py`, `external_benchmark_gate.py` and associated tests should be reused rather than rewritten.
- This is **offline model training and evaluation of existing approved candidate configurations**, not training an entirely new AI architecture, not recursive self-improvement and not 55 independent agents collaborating.
- Continue to require new explicit approval for any live workflow edits, paid API calls, secrets, independent agent activation or production changes.


## 9. Internal promotion-safety repair and independent-validation boundary (Nov 24, 2026)
- **Do not repeat completed Milestone 25**: three bounded model fits already produced internal validation results, detailed in section 8.
- Found and repaired a misleading historical field in `model_improvement_experiment.py`: its old `promotion_approved` could become true on internal handcrafted validation/test scores alone. It now emits `research_candidate_eligible` for this preliminary signal and forces `promotion_approved=false`. Its regression test now enforces that split. Research branch only; no live workflow or production changes.
- Verified offline CI https://github.com/rafa8525/consensus-project/actions/runs/45502177405: **365/365 tests passing**, commit `b6deb4a3234ad44afa679526a4b63c252df9345b`; report shows `research_candidate_eligible=true`, `promotion_approved=false`.
- Reused the existing replicated evaluator rather than rebuilding it. Latest report shows internal cross-validation macro-F1 delta **0.090667**, but **`replication_gate_passed=false`** and promotion remains blocked. The confirmation sample is hand-authored, so external generalization remains unproven.
- The external intake gate exists but only checks **declared** provenance and exact-string leakage. The project's three custom labels need an **independently labeled, licensed** external dataset; unrelated CLINC150/OOD labels cannot be treated as those three classes.
- Read `research/agi_iteration001/INDEPENDENT_VALIDATION_READINESS_20261124.md` for the frozen model comparison, data provenance and annotation requirements, and the next separate approval boundary before importing new third-party labeled data or promoting a model.
- **No new paid API calls, no GitHub live-workflow dispatch/re-pin, no production changes or agent activation** in this repair. Original successful API proposal remains certified and never needs replay merely to demonstrate connectivity.
