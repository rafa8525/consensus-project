# Milestone 14 — CI-verified frozen-threshold four-label holdout gate

**GitHub Actions:** https://github.com/rafa8525/consensus-project/actions/runs/44685154251  
**Verified code commit:** `c6603f2dc74dc3e1f57192736d489cf9ee408e8b`  
**CI status:** 138 automated tests passed, no failures; agent inventory validator confirms 55 unique **proposed** roles, zero production enabled.

## Implemented
The evaluator `milestone14_holdout_gate.py` freezes the word-model threshold at 0.15 and the character-trigram candidate threshold at 0.50, trains both only on the original 18 examples, and reads any separately provided four-way research-domain JSONL holdout with labels `design_experiment`, `evaluate_evidence`, `review_hypothesis`, and `out_of_scope`. Reports in-domain correct acceptances, OOD false acceptances, and four-way macro-F1.

Mechanical protections: SHA-256 checksum, byte/row bounds, minimum 10 samples per label, two distinct *declared* reviewers, declared source and license information, annotation protocol reference, and normalized exact-duplicate detection against all previously authored experiment samples. Tests include failures for missing attestations, duplicate samples, checksum tampering, symlinks and already-used phrases.

## Limitations and decision
This CI run tested the gate against **synthetic fixtures only**, not an independently sourced, genuinely labeled holdout. The provenance and reviewer fields are unverified declarations; the validator explicitly returns `human_provenance_independently_verified: false`, `promotion_approved: false`, `production_changes: false`. Any actual source and labeling independence must be validated independently and out of band. Near-duplicates and semantic leakage are not detected just by normalizing exact text.

**Decision:** gate implementation verified; no independent four-label benchmark performance result; no model promoted; no 55 operational agents deployed; no AI Consensus production changes.

**Next:** independently source a licensed, four-way labeled research task dataset, audit labels and source permissions separately, check semantic leakage, pre-register primary metrics and a decision threshold, run one frozen confirmatory test, then prohibit retuning on those results. Also begin measuring agent runtimes beyond simple label routing.
