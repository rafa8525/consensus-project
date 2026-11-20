# Milestone 18 — verified offline proposal admission

**GitHub CI:** https://github.com/rafa8525/consensus-project/actions/runs/44688825106  
**Exact verified source commit:** `463e8d0f9ecf32db0db0173faa4b8efefa722ee9`  
**Result:** 189/189 automated tests passed; registry continues to report 55 proposed roles, zero production-enabled.

## What ran

New `api_call_admission.py` performs offline `Approval` preflight with an explicit allowed model, declared project, finite decimal per-million token prices, bounded input/output ceilings, budget threshold, and live-call flags. A SQLite ledger reserves experiment IDs atomically to prevent duplicated simulated requests and stores SHA-256 hashes of validated proposals without persisting raw proposal texts. Simulated transport outputs pass the existing allowlisted structured proposal validator; rejection leaves a failed receipt. CI exercised valid, invalid and replayed flows.

A test with illustrative assumed prices of $1 per million input tokens and $2 per million output tokens plus 500/800 token ceilings calculates an estimated cost of $0.0021. **This is not actual model pricing, billing assurance, or an account-wide quota.**

## Important gaps

- These are **offline fake transport tests only**. The admission prototype is not wired to the existing opt-in OpenAI Responses adapter, and it does not make real API requests.
- The `Approval` dataclass is a self-declared Python object, not cryptographically signed or authenticated. The live-call flags are declarations; they do not independently verify billing configuration or user identity.
- Estimated token charges are not hard limits on actual dollar spend; tool/reasoning accounting, request pricing, and provider settings may differ.
- A per-file SQLite reservation is not globally shared across hosts or credentials; it cannot enforce billing project caps outside its own process.
- No novel architecture, independent model proposal, model generalization, recursive improvement, or AGI evidence was produced. The existing 3-role offline execution remains the baseline; 55 roles remain definitions only.
- No production ACS changes, API charges, secret provisioning or autonomous agent activation.

## Next substantive engineering priority

Rather than accumulating further admission gates, obtain a protected independently labeled capability benchmark for genuine multi-step reasoning and generalization, then implement a genuinely diverse model-proposal mechanism and compare its generated proposals with deterministic/random baselines under the same compute budget. Only after there is demonstrable benefit should the optional live provider and a real authenticated billing-aware execution service be enabled.
