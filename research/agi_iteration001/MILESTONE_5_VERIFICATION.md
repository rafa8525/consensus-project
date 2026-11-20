# Milestone 5 — offline model-worker end-to-end verification gate

This suite tests the **actual** research modules, not a mock of their behavior:
- train and save an offline classifier checkpoint
- validate the checkpoint before use
- assign a task to an AGI-role worker
- launch model inference through the persistent SQLite queue
- persist a result, label agreement and a message
- pass a prior worker's SHA-256 receipt to a dependent task
- reject unauthorized operations and corrupted checkpoints
- verify process-based CLI and database persistence

```sh
cd research/agi_iteration001
python3 -m unittest -v test_model_worker_integration.py
python3 -m unittest -v test_worker_runtime.py test_local_inference.py
```

**Verification protocol:** Commit the tests, then execute them in a clean checkout. Record Python version, SHA of the checkout, exit codes, test counts and any failures. Do not mark this milestone independently verified based solely on code review.

**Recovery safety:** A killed process can leave a task in `running`. Never automatically reassign that task based only on its age because another worker may still be alive. Require lease/heartbeat ownership and explicit bounded recovery rules before unattended retries. Avoid concurrent model workers in production until this is implemented.

**Model caveat:** 6 held-out examples are too few to demonstrate general-purpose reasoning. Train/test phrase overlap may inflate measured accuracy. Future experiments must compare with a majority-class baseline, use larger disjoint data and report multiple random splits.

**Deployment status:** Research branch only. No production ACS changes, API spending, 24/7 schedule or new cloud services.
