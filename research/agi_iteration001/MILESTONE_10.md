# AGI Milestone 10 — External-data gate and resource-metered robustness

The Milestone 9 confirmation advantage was uncertain (paired 95% interval included zero). This iteration does **not** claim a new independent data source, because one has not been obtained and reviewed.

Deliverables:
1. Frozen 12-item **internal** paraphrase stress suite for the word-only and character-trigram models; reports accuracy and macro-F1.
2. Training/inference wall-time and Python-traced peak allocations. `tracemalloc` does **not** measure process RSS or impose resource limits. Measurements vary by GitHub runner.
3. A fail-closed external JSONL intake validator: SHA-256, mandatory source URL/license/annotator/method, label balance, record limits, identical-text leakage detection against previous development/confirmation/stress items, and size bounds.
4. Tests with *synthetic fixture data*, clearly not independent external examples. Even an accepted manifest is only a **declaration**, not proof of its source or independent labeling. `independent_provenance_verified` and `promotion_approved` stay false.

Run from `research/agi_iteration001`:
```sh
python3 external_benchmark_gate.py
python3 -m unittest -v test_external_benchmark_gate.py
```
For external data, provide `--external-jsonl path --manifest path`. JSONL must contain exactly `{"label": "...", "text": "..."}` per line; manifest requires `sha256`, `source_url`, `license`, `dataset_id`, `annotator_id`, `collection_method`, `heldout_for: "research-task-classification-v1"`. Do not use data without permission/license review or publish private data in CI logs.

**Important limitation:** The agent registry's 55 names are *proposed roles*, not 55 autonomous AI workers. This benchmark is classification, not reasoning or foundation-model training. No production, scheduled, paid infrastructure, or model promotion changes.
