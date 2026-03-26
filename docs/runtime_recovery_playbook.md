# Runtime Recovery Playbook

## Goal
Recover runtime health safely without hanging the console, creating false alarms, or introducing broad regressions.

## Safe operating rules
Always follow these rules during runtime recovery work:

- use short, scoped commands
- do not run foreground loops unless explicitly intended
- inspect first, patch second
- avoid broad mass-replace operations
- use compile or syntax checks before restarts
- verify recovery with one monitor run and one proof read

## Standard preflight gate

### For Python files
Run:

    python3 -m py_compile <file>

### For shell files
Run:

    bash -n <file>

### After any runtime change
Run:

    bash /home/rafa1215/consensus-project/run_with_env.sh /home/rafa1215/consensus-project/tools/core_monitors_bundle.py
    cat /home/rafa1215/memory/logs/status/system_health_snapshot.md

A change is not considered complete until the health snapshot reflects reality.

## Recovery workflow
Use this order every time:

1. identify the exact symptom
2. inspect the live path or writer first
3. determine whether the issue is:
   - launcher drift
   - monitor drift
   - stale writer
   - path policy mismatch
4. make the smallest safe fix
5. run preflight validation
6. rerun the health monitor
7. record the result in the drift inventory

## Recovery case: launcher failure

### Symptoms
- `master_control_loop.py` does not come back after restart
- `master_control_loop.log` is stale
- `heartbeat.md` is stale
- `system_health_snapshot.md` shows orchestrator or heartbeat warnings

### Checks
1. confirm launcher points to:
   - `tools/master_control_loop.py`

2. verify there are no legacy references to:
   - `~/consensus-project/master_control_loop.py`

3. syntax-check the launcher:
   - `bash -n start_all.sh`

4. if needed, start the loop safely in the background

### Proof of recovery
Recovery is confirmed only when:
- `master_control_loop.log` is fresh
- `heartbeat.md` is fresh
- monitor output reflects those fresh files
- `Overall` returns to `ok` or remaining warnings are real

## Recovery case: false monitor warning

### Symptoms
- health snapshot shows `warn`
- the underlying writer is actually healthy
- the monitor is checking the wrong path or wrong filename

### Typical causes
- `.md` vs `.txt` mismatch
- repo-local memory vs canonical memory mismatch
- monitor assumes a stale legacy path

### Checks
1. inspect the actual writer output path
2. compare the monitor path to the real path
3. compare expected filename to actual filename
4. patch the monitor when the writer is already correct
5. rerun the monitor

### Rule
Do not rewrite a healthy writer just because the monitor expects the wrong file.

## Recovery case: stale writer

### Example stale writers
- `knowledge_base_status.log`
- `movies_monitor_status.json`
- `weekly_status_report.txt`
- `heartbeat.md`

### Recovery steps
1. identify which script writes the stale file
2. run that writer once manually
3. verify the file timestamp changed
4. rerun the health monitor
5. determine whether the writer needs better scheduling or orchestration coverage

### Proof of recovery
Recovery is confirmed only when:
- the file timestamp is fresh
- the health snapshot reflects the fresh file
- the warning clears or becomes more accurate

## Recovery case: path drift confusion

### Symptoms
- repo-local files are fresh
- canonical-memory files are stale
- the monitor reports stale status even though the system is running

### Checks
1. inspect both roots:
   - `~/consensus-project/memory/...`
   - `/home/rafa1215/memory/...`

2. determine whether the split is intentional
3. patch monitors or launchers surgically
4. do not mass-replace `/home/rafa1215/memory` references across the repo

### Rule
A split-path design may be intentional. Confirm policy before changing code.

## Recovery case: health green but architecture unclear

### Symptoms
- health is `ok`
- runtime is working
- path usage still feels confusing

### Response
Do not change working code immediately.

Instead:
1. document the current behavior
2. update the path policy
3. update the drift inventory
4. schedule a small audit later if needed

## Runtime proof checklist
A runtime fix is only considered complete when all of the following are true:

- the changed file passes syntax or compile validation
- the relevant writer or launcher behaves correctly
- `core_monitors_bundle.py` runs cleanly
- `system_health_snapshot.md` reflects reality
- root cause and repair are documented

## Git hygiene during recovery
During recovery work:

- commit source, config, and doc changes only
- avoid bulk-committing volatile logs unless explicitly intended
- use focused commit messages
- preserve known-good repairs as soon as they are verified

## Verified lessons from 2026-03-23
The runtime recovery on 2026-03-23 established these lessons:

- launcher path drift can make a healthy system appear dead
- false monitor warnings can hide the real remaining failures
- repo-local vs canonical-memory splits must be handled intentionally
- stale writers should be revived individually and verified one at a time
- recovery works best when commands are short, scoped, and safe for the console