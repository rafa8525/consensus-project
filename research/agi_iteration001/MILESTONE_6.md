# Milestone 6 — bounded leases and fenced recovery (research prototype)

Files: `leased_worker.py`, `test_leased_worker.py`.

The module is an **isolated alternative queue**, not a modification of the earlier `worker_runtime.py` or `model_worker.py`. It implements transactional claims, expiring leases, owner heartbeats, two-attempt retry limits, and fenced completion. Older workers cannot write results after their leases expire. Expired leases can cause redundant computation; **exactly-once external side effects are not guaranteed**. Only side-effect-free model classification is permitted at this stage.

The model adapter accepts a *previously integrity-verified* checkpoint and prediction callback; this module does **not** train a model. A production deployment must call `local_inference.load_checkpoint` before using `model_job`. No live deployment or unattended scheduler has been configured.

Local independent prototype exercised 13 tests on 2026-11-19. A closely equivalent, simplified committed suite contains 14 tests and requires a clean checkout test run before that committed suite is certified. Do not substitute local test success for CI evidence.

Run `python3 -m unittest -v test_leased_worker.py` from this directory.

Important remaining gaps: independent clean-checkout execution, checkpoint integration test against `local_inference.py`, input resource isolation (CPU/memory), liveness/heartbeat scheduler, production recovery integration and failure alert routing. No modifications to ACS-01..05, cloud resources, branch `main`, or Phase 1 certification.
