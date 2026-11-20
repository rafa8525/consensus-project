# Milestone 18 — research-model call authorization simulation

Research-only admission checks and a persistent one-call ledger are implemented in `api_call_admission.py`. CI tests approved-model matching, nonnegative finite per-million token pricing, worst-case **estimated** cost against a declared per-experiment budget, finite token caps, distinct authorization flags, no unapproved live-call enablement, and atomic refusal of replayed/reserved experiment IDs.

`run_mocked_proposal()` uses a supplied fake callable and **never makes a network/API request**. It records only a SHA-256 of the accepted structured proposal in SQLite, not the proposal text or credentials. Malicious or malformed output yields a failed receipt; duplicates cannot retry invisibly. This is a simulated preflight, *not yet attached to the live Responses API adapter*.

**Limitations:** developer/operator-supplied approval records can be forged in Python and do not prove identity; a cost estimate using token ceilings is **not** a guaranteed billing cap (input token counting, pricing changes, reasoning charges, retries and billable usage can differ). Rate controls are per-ledger, not account-wide. This module cannot authorize real model calls or prevent other code from calling APIs. Obtain independently verified project billing settings, a real secret vault, a mutually authenticated execution boundary, and a legitimate budget-enforcement service before enabling any live experiment.

This milestone is an engineering safeguard, **not** general intelligence advancement. No independent novel model designed, no 55 active agents, no genuine model API usage, no production changes.
