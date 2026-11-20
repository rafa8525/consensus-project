# Milestone 13 — development-only out-of-domain rejection calibration

The Milestone 12 evaluation examined all 1,000 `oos_test` samples, so **those samples are now exposed and cannot be used again for unbiased hyperparameter selection or fresh confirmatory testing**.

This iteration fetches the same SHA-256-pinned original CLINC150 data but reads **only `oos_val`** to select a vocabulary-coverage acceptance threshold separately for the two fixed trained classifiers. It combines the in-domain correct-acceptance fraction on the existing 12-item validation set with the out-of-domain rejection fraction on `oos_val`, giving each equal weight, and searches a fixed threshold grid (0.05 to 0.95 in 0.05 increments). In-domain data are hand-authored and already exposed, so this is exploratory development, not clean external verification.

The prior 18-item confirmation set is reported purely for context; it too was already seen. The protocol deliberately does not inspect `oos_test` during threshold selection. The research model is **not** promoted even if development metrics improve.

CLINC out-of-scope labels were defined relative to CLINC150's 150 intent classes, **not** the three labels in this project. The OOD interpretation remains a proxy. A new independently curated and labeled, research-specific holdout is needed for model promotion.

Source: Larson et al., EMNLP 2019, https://aclanthology.org/D19-1131/ ; original repository https://github.com/clinc/oos-eval (CC BY 3.0 Unported in upstream LICENSE).

No prod code, spending, secrets, 55-agent deployment or scheduling changes. 
