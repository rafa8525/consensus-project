# Milestone 16 — Offline proposal-provider integration

Implements the first bounded integration step from ADR-016. We preserve the prior v1 three-role cycle as the baseline.

## Exact scope
- `proposal_provider.py` defines a strict allowlist for the structured experiment plan: one word-NB baseline, two existing character-ngram variants, approved metrics/datasets, bounded fit count and stop conditions.
- `OfflineProposalProvider` is a **recorded, deterministic fake provider**. It is *not* an LLM and cannot formulate novel research hypotheses. No network/API provider is enabled.
- `three_role_provider_v2.py` binds the validated offline proposal to the real three-role SQLite pipeline. The engineer trains three actual small classifiers, and the independent evaluator recomputes all development metrics. Immutable receipts survive re-running. Previously used confirmation results are descriptive, never proof of better generalization.
- Unit tests reject unexpected fields, executable-looking instructions, changed datasets, changed architectures, larger budgets, duplicate proposals, tampered receipts and purported live providers. Failure of unsafe proposals happens before any DB is created.
- CI runs the offline end-to-end scenario, never accesses paid APIs, keeps the data within the ephemeral runner, and blocks any model promotion.

## Important limitations
This is **integration scaffolding**, not AI-backed agents or recursive self-improvement. The model candidate set remains identical to previously tested examples; 18 training and 12 validation examples are too small to justify generalization. The three roles are deterministic and the 55 registry entries remain proposed, not operating agents.

Next engineering milestone: attach a live, explicitly authorized and budgeted model-backed proposal provider under the same schema and allowlisted execution policy; conduct a novel, independently reviewed research benchmark before claiming improvement. Consider independent oversight for proposal provenance and resource consumption.

No production changes or additional compute services authorized.
