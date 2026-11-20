# Milestone 3: Executable research worker prototype

**Status:** Research branch only, not deployed. The 55-role registry remains disabled for production.

`worker_runtime.py` implements a durable SQLite work queue. A worker launches as an **actual OS subprocess**, claims one eligible role-specific task, performs a deterministic bounded research-checklist operation, and records a content-hashed result and a message. A dependent task can read the earlier digest. These are **not 55 independent LLMs**, nor are the deterministic checklists intelligent autonomous research or model training.

## Reproduce locally
From `research/agi_iteration001`:
```sh
python3 -m unittest -v test_worker_runtime.py
python3 worker_runtime.py --db ./scratch.sqlite init
```
To run a task, create a task JSON with keys `id`, `agent_id`, `operation`, `objective`, and `dependencies`, then:
```sh
python3 worker_runtime.py --db ./scratch.sqlite enqueue --task-file ./task.json
python3 worker_runtime.py --db ./scratch.sqlite worker-once --agent AGI-01 --worker-id w1
python3 worker_runtime.py --db ./scratch.sqlite status
```
Run in a dedicated unprivileged research container and keep SQLite files outside the production repository.

## Constraints and limitations
- Only `review_hypothesis`, `design_experiment`, `evaluate_evidence` deterministic operations
- Up to 55 tasks per database and five dependencies per task; no external commands, API calls, cloud mutation, or model inference
- Transactional task claims, append-only messages, persistent results, and duplicate-task rejection
- Two separate child processes were exercised in the local test suite; no 55-process deployment has occurred
- No unattended scheduler, autonomous retry after crash, lease expiry, resource isolation, or production health integration yet
- Running task interrupted by process death remains `running` and needs supervised remediation
- SQLite is a local queue prototype, not a hardened distributed task broker

## Safety / deployment gate
Keep ACS-01..05 and existing Phase 1 certification wholly separate. Resolve ACS-03 and ACS-05 problems and verify machine capacity before any background workers or expanded deployment. Independent reproduction and security review required.
