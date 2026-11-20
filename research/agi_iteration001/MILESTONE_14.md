# Milestone 14 — Frozen, independently labeled research-domain holdout gate

## Intent

Milestone 13 selected word-only NB acceptance threshold **0.15** and trigram NB threshold **0.50** on *development-only* CLINC150 `oos_val` and an already exposed hand-authored validation set. This milestone freezes both thresholds and the pre-existing 18-example training set so an actual independent **research-domain** test can be executed later without hidden retuning.

## Implemented

- `milestone14_holdout_gate.py`: accepts labeled UTF-8 JSONL from **four explicit labels** (`design_experiment`, `evaluate_evidence`, `review_hypothesis`, `out_of_scope`).
- At least 10 examples per class; size and normalization/duplication bounds; rejects exact normalized overlap against all previous manually authored train, validation, test, confirmation and stress inputs.
- Manifest requires SHA-256, HTTPS source URL, license, collection method, annotation guidelines link and two different reviewer identifiers, as well as explicit training/validation exclusion declarations.
- Reports in-domain correct-and-accepted counts, out-of-domain false-accept rate, and four-way macro-F1. Existing model/thresholds are frozen. **No promotion whatsoever**.
- Unit tests use an entirely *synthetic fixture* with fabricated provenance fields. That is a protocol test, **not** proof that a source/reviewer or independent test was obtained.

## Correct usage

```sh
python3 milestone14_holdout_gate.py --holdout-jsonl independently_reviewed.jsonl --manifest provenance.json
```

Input manifest keys: `sha256`, `source_url`, `license`, `dataset_id`, `collection_method`, `annotation_guidelines_url`, `reviewer_1`, `reviewer_2`, `review_utc`, `training_data_excluded: true`, `validation_data_excluded: true`. These declarations are **not identity, license, or independent provenance verification**. A separate human-led review of the original source and label agreement remains required. Do not publish raw private user texts or annotation identifiers.

An independently labeled, licensed, on-domain four-label holdout was not available during this iteration, so no confirmatory numerical accuracy or promotion claim is possible. No 55-agent fleet execution or production runtime changes are claimed.

The isolated CI verifies the gate with synthetic fixtures only; it does not execute it on a real holdout. The main purpose is safeguarding the experiment against reuse of exposed test data and unsupported upgrades.
