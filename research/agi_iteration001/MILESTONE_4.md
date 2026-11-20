# Project AGI — Milestone 4: offline trained inference adapter

**Status: Research branch, no production deployment.** Adds `local_inference.py` (standard-library multinomial Naive Bayes) and `model_worker.py` (adapter for `worker_runtime.py` SQLite queue).

Train offline from this directory:
```sh
python3 local_inference.py --checkpoint /tmp/agi-iteration001-classifier.json
python3 -m unittest -v test_local_inference.py
```
This trains on 18 hand-authored short research-task phrases (six per label) and evaluates on six held-out phrases (two per label). Local execution on 2026-11-19 reported **6/6**, with eight independent *test cases* passing locally. The test phrases overlap in vocabulary/theme with training phrases; this is a small smoke test, **not** proof of broad generalization. The classifier is not a language model or reasoning model.

To use with the existing local queue in a separate test environment, first initialize a queue and enqueue a task via `worker_runtime.py`, then:
```sh
python3 model_worker.py --db /tmp/agi-test.sqlite --checkpoint /tmp/agi-iteration001-classifier.json --agent AGI-01 --worker-id model-worker-01
```
This records the model-predicted task category and confidence distribution as a result and an SQLite message. It does not alter the task's original authorized operation and it does not authorize new operations. It does **not** perform research or model training autonomously. The adapter's end-to-end integration with the exact GitHub queue has not yet been independently reproduced.

**Controls:** no cloud API, no credentials, no paid inference provider, no network activity; validated checkpoint SHA-256, explicit model label set, 500-character inference input cap. Existing worker runtime's resource/isolation limitations still apply, including no crash lease recovery and no production scheduler.

**Deployment gate:** ACS-03/ACS-05 reported unhealthy in the latest inspected health snapshot (2026-11-19T18:03:09Z). Verify up-to-date production health, resource limits, sandbox controls and integration tests before enabling background workers.
