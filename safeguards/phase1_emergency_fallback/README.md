# Phase 1 emergency restoration — NOT DEPLOYED

This is a **manual, independent-host fallback** for PythonAnywhere scheduled task `1524414`. It does not run on GitHub Actions, is not scheduled, and cannot demonstrate unattended production recovery. Nothing in this branch modifies `main`, a running scheduler, a token, or Google Cloud.

## Deployment prerequisites

- A separate Google Cloud host accessible to the operator, with Python 3, HTTPS egress to the PythonAnywhere API, and a non-committed token stored privately.
- A privately transferred backup `phase1_original_acs01_schedule.json` from the PythonAnywhere host, mode 0600. **Never commit the backup or token.**
- Operator access to PythonAnywhere Tasks as a last resort.
- Separate approval before granting an unattended process permission to issue any PATCH. This version is **manual only**.

## Staging / dry-run (read-only)

```bash
python3 -m unittest -v test_acs01_emergency_restore.py
python3 acs01_emergency_restore.py --baseline /private/path/phase1_original_acs01_schedule.json
```

The CLI reads current scheduler status; it never writes without `--restore --confirm RESTORE-ACS01-1524414`. Do not invoke that restoration command unless an actual disabled task has been identified and restoration has been approved. There is **no** `enabled:false` operation in the utility.

## Preconditions for any future controlled live experiment

1. Reconfirm task `1524414` is enabled, healthy, and identical to its private backup apart from known API timestamps.
2. Have operator access to both PythonAnywhere Tasks and the separate fallback host.
3. Set a written restoration deadline. Verify the fallback can read the API without changing anything.
4. Do not run an active fallback that races the primary scheduled guard.
5. Explicitly authorize any test that disables the production scheduler; that authorization has not been given.
6. Independently observe state, action, and subsequent health publication, and preserve redacted evidence.

## Limits

A GitHub runner or PythonAnywhere API outage can outlive a test. A manual fallback is not an autonomous second watchdog; do **not** claim independent unattended recovery until a separately executed and verified scheduler exists. A successful re-enable is not proof of process-crash recovery. PR #37's production-outage acceptance criteria remain unmet.

The code rejects task identity/command drift, unexpected fields, maintenance, and unconfirmed restoration; prints no secrets or commands. Automatic retry on API errors is intentionally absent: manual operator intervention is safer than assuming unknown provider state.
