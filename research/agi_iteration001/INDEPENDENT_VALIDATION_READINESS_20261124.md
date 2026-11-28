# Independent evaluation readiness / Phase 2 gate (2026-11-24)
Status: **BLOCKED ON INDEPENDENT LABELED TASK DATA AND PROVENANCE REVIEW**.

## Completed, do not repeat
- API integration succeeded: paid run https://github.com/rafa8525/consensus-project/actions/runs/45499920454. Exactly one model-generated proposal was validated. The prose was not retained, so subsequent offline work uses a *fixed approved fixture* rather than pretending to replay the original.
- Three-fit offline evaluation passed: https://github.com/rafa8525/consensus-project/actions/runs/45501425963. Small hand-authored validation macro-F1 was 0.481818 for word NB and 0.742857 for each character candidate. The selected 3-gram candidate is a preliminary local result, **not verified external generalization**.
- Promotion safety fix passed: https://github.com/rafa8525/consensus-project/actions/runs/45502177405. The earlier `model_improvement_experiment.py` could set `promotion_approved=true` solely on internal handcrafted tests. It now emits `research_candidate_eligible` separately and forces `promotion_approved=false`. 365/365 tests passed. This is a research-branch-only change.
- Existing replicated evaluation was *already* in the project. Latest CI reports `cv_macro_f1.delta=0.090667`, but `replication_gate_passed=false`, and `promotion_approved=false`. The 25 cross-validation folds are correlated, not independent experiments; the confirmation corpus was also hand-authored.
- Existing `external_benchmark_gate.py` already supports a manifest-checked dataset intake: checks SHA256, HTTPS source claim, declared license/annotator/collection details, at least 30 records with at least 8 per class, exactly the three task labels, duplicates and internal-leakage checks. This code **does not itself verify that provenance declarations are true**. The independent-provenance gate remains closed.

## Critical external-validation constraints
1. The trained classifier targets **three custom task-intent labels**: `design_experiment`, `evaluate_evidence`, `review_hypothesis`. An unrelated public intent dataset such as CLINC150 OOD is NOT a labeled evaluation set for these classes. Do not relabel categories by guesswork and call them independent.
2. Before acquiring an external corpus, document the exact licensing permissions, source URL, collection dates, reviewable annotator/labeling protocol, and dataset version and checksum. Do not copy private material or user credentials into the corpus.
3. Use an independent annotator or documented independent ground truth for each class. Require at least 30 fresh examples, >=8 per label, with no exact or normalized overlap against training, validation, historical holdout, confirmation and stress sets. Inspect for near-duplicates and common source contamination too; code currently only rejects exact normalized matches.
4. **Freeze** candidate `word_char_nb, n=3, alpha=0.5` and word NB baseline before looking at independent labels. Use already-reviewed measurement code, one confirmation comparison, macro-F1 and paired uncertainty; do not retune on the independent set.
5. Report the absolute scores, paired sample size, uncertainty and failure cases, separately from the internal CV and 12-example validation gain. Even good external scores do not authorize deployment automatically.
6. Require **human provenance verification and separate explicit promotion approval**. A manifest containing `source_url` and `license` is not authoritative evidence by itself. Keep independent_provenance_verified=false until reviewed.
7. No paid API calls, auto-dispatch, workflow re-pinning, production activation, secret handling or 55-agent execution are part of this phase.

## Suggested bounded next authorization boundary
Prepare the proposed independent dataset source, license and annotation plan **for human review** before creating/committing new third-party data or introducing new network dependencies into CI. Existing internal test and model-training work is already demonstrated; do not repeat it just to increase test counts.

## Current software limitation
The project uses a single hand-written corpus and small classical classifiers. These results cannot establish novel AI architectures, recursive intelligence improvements or AGI. All 55 roles are registry definitions; they are not automatically independent operating agents.
