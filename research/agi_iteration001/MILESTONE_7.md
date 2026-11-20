# Milestone 7 — clean-run verification and leased model integration

The new `leased_model_worker.py` combines `leased_worker.py` with the existing offline classifier. The checkpoint is loaded with its checksum validated **before** claiming work. Claim and completion use a 30-second lease and fencing token. The adapter performs only one local inference per invocation and does not deploy, schedule, retrain or launch an autonomous agent.

`test_leased_model_worker.py` adds seven integration cases: successful inference, empty queue, corrupt checkpoint, invalid role, crashed claim recovery, retry exhaustion and a separate CLI subprocess.

`.github/workflows/agi-research-verification.yml` adds a branch-scoped, read-only CI test run covering previous and new research suites. The workflow uses GitHub-hosted runner capacity; it **does not** access cloud VMs, PythonAnywhere, secrets or production services, and cannot enable paid external infrastructure. GitHub Actions usage is subject to the account's existing plan/quotas.

## Remaining limitations
- Leases are not a runtime resource sandbox; OS-level CPU, memory and network restrictions remain to be implemented.
- Database operations alone cannot prevent duplicate arbitrary side effects, so inference must remain side-effect-free.
- A worker crash leaves the lease running until explicitly reclaimed; no unattended controller is deployed.
- The small task classifier is not an LLM, not independent reasoning, and not evidence of AGI.
- CI result must be checked before marking verification complete. Committed code does not equal an executed passing test.
- No production deployment until ACS-03/05 issues are resolved and independent health and compute verification are complete.
