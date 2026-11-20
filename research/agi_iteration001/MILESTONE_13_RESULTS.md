# Milestone 13 — verified OOD rejection calibration

**GitHub CI:** https://github.com/rafa8525/consensus-project/actions/runs/44684764056
**Verified code commit:** `affb081273852569dab852f3cddcf5c400e140a8`
**CI:** 125/125 automated tests passed, 55 proposed roles validated, none production enabled.

## Experiment protocol
Used pinned original CLINC150 `data_full.json` SHA-256 `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`.
Calibrated each model's vocabulary-coverage acceptance threshold on **100 `oos_val` items only** and 12 existing hand-authored in-domain `VALIDATION` items. Scanned a fixed grid of thresholds 0.05..0.95 in increments of 0.05, optimizing equal-weight mean of in-domain correct-acceptance fraction and OOD rejection fraction.

**Crucial:** The previously examined `oos_test` (1000 examples) was not read by the calibration module or run in CI during this iteration. The prior 18-item confirmation examples have been exposed and are descriptive only.

| Development metric | Word-only NB | Word + character trigram NB |
|---|---:|---:|
| Selected threshold | 0.15 | 0.50 |
| `oos_val` rejected | 95/100 | 96/100 |
| In-domain validation correctly classified AND accepted | 6/12 | 9/12 |
| Balanced objective | 0.725 | 0.855 |
| Exposed 18-item confirmation correct AND accepted | 9/18 | 11/18 |

**Model-fitting detail:** Both research classifiers in this calibration are trained on the original 18-row `TRAIN` split; `VALIDATION` is used to select the abstention threshold. This differs from Milestone 12's retraining on the combined 30-row `DEVELOPMENT` split, so metrics are not directly comparable.

The old common 0.25 threshold was not calibrated to different feature spaces. The new per-model thresholds address that methodological weakness *on development data only*. There is no new untouched research-domain test set, and CLINC `oos_val` uses OOD labels relative to CLINC's 150 classes. Model promotion is **blocked** (`promotion_approved=false`).

No production updates, model replacement, money spent, agent activations, credentials, or cloud changes. The 55 roles remain registry entries, not 55 running AI agents.

**Next step:** Freeze these thresholds, obtain independently labeled research-domain in-scope and out-of-scope tasks from a different source, and run one confirmatory test without tuning afterward. Analyze coverage/rejection tradeoffs and failure costs with confidence intervals.
