# Milestone 24 — Verified frozen symbolic program out-of-language stress

**Preregistration:** `MILESTONE_24_PREREGISTRATION.md`, commit `38c16ae2b1165031a0915731693b5a7ca8aabf58`, written before benchmark and tests.  
**Verified source commit:** `3b737cf212d4ff80f8b07e20a72ccf20428cb9e0`  
**Successful GitHub Actions run:** https://github.com/rafa8525/consensus-project/actions/runs/44800951139  
**CI:** 256/256 tests pass; 55 distinct proposed roles, zero production-enabled.

## Frozen evaluation

The same Milestone 23 exact program search (affine, square, interaction) sees 8 demonstration examples. Three in-language families (10 tasks each) and two not-in-DSL families (15 tasks each: mixed quadratic-interaction and conditional nonlinearity) were generated from disjoint new seeds. 16 queries each = 960 withheld queries total. A no-consistent-program outcome abstains; comparison forces majority-label fallback where no exact rule can be found.

| Population | Tasks | Accepted by matching fixed DSL | Abstained | Correct accepted predictions | Forced fallback correct predictions |
|---|---:|---:|---:|---:|---:|
| Known 3 families | 30 | 30 | 0 | 480/480 | 480/480 |
| Unsupported 2 families | 30 | **0** | **30** | 0/480 (not answered) | 50/480 |

Out-of-language false acceptance is 0/30 **in this narrow, generated trial**; in-language acceptance is 30/30. The unguarded forced-fallback option makes 430 incorrect predictions on unsupported queries while the guarded model declines to answer. However, abstaining is not the same as solving the problems: coverage-adjusted accuracy counts all 480 out-of-language queries unanswered/incorrect. This is a *rejection capability*, not a general-purpose learning improvement.

## Limitations

These are five prechosen mathematical families in a bespoke generator. Out-of-DSL examples were designed to challenge this specific hypothesis language; false acceptance can still arise on other unsupported tasks when an incorrect program happens to fit 8 demonstrations. Rule search is deterministic enumerative software, not autonomous AI or neural learning. The evaluation is internally generated and now exposed; no independently sealed external benchmark was used. No general intelligence or novel algorithm invention has been demonstrated.

## Genuine next approval boundary

The next substantive experiment requires a **live model-backed proposal generator** to compare against these offline scripted baselines on a yet-unseen evaluation family and under controlled resource usage. The optional Responses adapter was implemented in M17 but remains disabled in the three-role executor. M18's cost estimate and SQLite reservations are **not a real account-wide USD cap or authenticated approval**.

Before proceeding with actual live API calls: obtain the user's explicit authorization for a model, finite spending amount, secured API credentials on a dedicated OpenAI API project, and independently verified account/project billing controls. Never ask the user to paste private API keys in chat; never assert that an OpenAI API project has a strict guaranteed hard-dollar cutoff without verification. Keep all GitHub research code in the isolated branch with no production ACS or auto-merge changes.

**Current status:** all permitted offline research work completed up to approval boundary, no OpenAI API charges, no production changes, model promotion disabled, 55 agent definitions remain proposed only.
