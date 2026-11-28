# Milestone 16 — CI-verified offline proposal-provider V2

**Verified CI run:** https://github.com/rafa8525/consensus-project/actions/runs/44687955816  
**Exact verified source commit:** `6eacc9c12b0b4df0ff53caece9486308e1356de8`.  
**Result:** 168/168 automated tests pass; GitHub Actions checked matching commit SHA. Agent registry validation: 55 unique **proposed** role definitions, zero production enabled.

## Deliverables
- `proposal_provider.py`: deterministic offline proposal generator; strictly validated hypothesis, falsifier, objective, dataset ids, compute budget, exactly one baseline + two allowlisted character n-gram variants and fixed stop rules. Rejects malformed JSON, unexpected fields, executable-looking instructions, altered test datasets, arbitrary model code, oversized budgets and duplicate variants.
- `three_role_provider_v2.py`: invokes validated planner proposal, trains three small actual Naive Bayes variants through the existing deterministic model engineer, independently recomputes validation metrics through the existing evaluator and records three hash-checked SQLite receipts.
- `test_three_role_provider_v2.py`: unit and end-to-end tests for invalid inputs, hard limits, idempotence, tamper rejection and disabled live providers.
- The existing deterministic V1 research cycle remains unchanged and continues running in CI. All experiments remain on the isolated research branch.

## What the evidence does and does not establish
- The offline stub produces a fixed proposal. **No live OpenAI API or other model-backed planner has yet been invoked**; no new independently invented model architecture has been generated.
- The model search space consists of three previously evaluated variants on an already-exposed, tiny hand-authored dataset. The previous confirmation results are *not* independent scientific proof of improvement.
- The evaluator reproduces the calculation, and `promotion_approved=false`. The 55 registry entries remain proposed roles, **not 55 functioning agents**.
- The code makes no paid API calls, uses no production credentials, and makes no production ACS changes.
- The approach is a credible *interface and execution foundation*, but not yet AGI or measurable recursive intelligence growth.

## Next research milestone
1. Independently source and label a challenging research-task holdout, with validated provenance and protected release conditions.
2. Introduce opt-in model-backed planner via explicit API configuration and strict budget controls, testing only structured proposal output, never generated executable code.
3. Expand the model search space carefully to meaningful learning algorithms, and adopt capability benchmarks for reasoning and transfer beyond text classification.
4. Compare proposed experiments against a deterministic/random proposal baseline; independently reproduce each result; report failures, resource cost, and human interventions.

No deployment or compute spending is authorized by this report.
