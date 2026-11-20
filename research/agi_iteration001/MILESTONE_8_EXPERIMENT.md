# AGI Milestone 8 — controlled model-improvement experiment

Goal: move beyond reliability engineering to an actual, measurable model design/train/test iteration.

**Hypothesis:** a character n-gram + unigram multinomial Naive Bayes classifier may generalize to morphological variants of research-task descriptions better than the existing word-only Naive Bayes baseline.

- **Train:** 18 existing hand-authored research tasks, six per role class.
- **Validation:** 12 new disjoint descriptions, four per class. Select among 9 feature settings (character sizes 3/4/5 × smoothing 0.5/1/2).
- **Test:** 12 disjoint descriptions, four per class, assessed only after validation selection. The original six illustrative held-out examples are not used for this tuning gate.
- **Metrics:** correct counts, accuracy, per-label confusion.
- **Gate:** candidate must *strictly* exceed baseline on validation and not regress on independent test to be marked preliminarily promotable. Otherwise record **no improvement**; never silently promote.
- **Reproducibility:** dataset SHA-256, deterministic feature extraction, fixed splits; outputs printed as JSON.
- **Scope:** research-only, no runtime changes. Approval is only for a candidate research checkpoint, *not* deploying a model, claiming AGI, or launching 55 operational agents.

Run:
```sh
cd research/agi_iteration001
python3 model_improvement_experiment.py
python3 -m unittest -v test_model_improvement_experiment.py
```

This is a deliberately small scientific smoke test. Hand-authored lexical patterns, single split and a 12-example test cannot establish generalization. Next cycle must add an independent real-world evaluation dataset, multiple train/test seeds or splits, uncertainty intervals, CPU/memory measurement, and independent hypothesis reviewers before any autonomous recursive optimization.
