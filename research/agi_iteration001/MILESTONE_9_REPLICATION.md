# AGI Milestone 9 — Replication gate before model promotion

This iteration strengthens the original 18-example word-NB baseline versus the trigram-NB candidate. There is **no claim of general intelligence**.

**Protocol:** The model selected in Milestone 8 is frozen at n=3, alpha=0.5. Combine original training (18) and original validation (12) examples for *development only*; do not reuse the prior 12-example test for fitting or hyperparameter selection. Perform five random-seeded stratified 5-fold runs (25 folds in all). Report average macro-F1. Train both models on the same fold training set and evaluate on the same fold test set. Then retrain both on all 30 development records and score a new fixed 18-example hand-authored confirmation set, assessed once.

**Guardrails:** Confirmation is a new hand-authored dataset, not a verified independent external benchmark; lexical overlap and selection bias remain. The folds share examples, so their results are correlated. A 1,000-resample paired percentile bootstrap on confirmation accuracy illustrates small-sample uncertainty. Even if a predefined replication gate is met, `promotion_approved` remains false without independently sourced replication. Tests run on the research branch without network calls, production writes or model replacement.

**Gate:** Require mean CV macro-F1 gain >=0.05, >=2 more correct examples on confirmation and a strictly positive lower bound of the paired bootstrap difference. Also require independently sourced validation before promoting. No automatic production promotion.

Run:
```sh
python3 replicated_model_evaluation.py
python3 -m unittest -v test_replicated_model_evaluation.py
```

Research limitations: 30 development examples / 18 confirmation examples across three classification labels, not new foundation-model pretraining; no 55 agents actually executing these studies yet; compute resource metering and external dataset sourcing still pending.
