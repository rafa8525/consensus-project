# Private-runtime ACS diagnostic — read-only and redacted

`acs_private_triage.py` adds a local diagnostic that inspects existing ACS-03/05 state files and the timestamp/validity of genuine fitness inputs without printing personal metrics, raw logs, OAuth credentials, Twilio numbers, or exceptions. It does not execute any ACS cycle, repair, send messages, or change filesystem state. The output remains metadata only.

## Local invocation
```sh
cd ~/consensus-project/research/agi_iteration001
python3 acs_private_triage.py --repo ~/consensus-project
```

**This is not deployed.** Do not run on production without first confirming the research branch code is present, reviewed and permitted. The private-runtime result must be compared with current ACS state and a freshly published report. The cloud-cycle script uses a private path, so its exit code is still insufficient to diagnose the exact cause. The report intentionally does not expose actual guardian messages; authorized operators must review those privately.

## Repair criteria
- ACS-03 must have genuinely current fitness input and successful cloud-cycle execution; do not create synthetic health measurements or rewrite timestamps.
- ACS-05 must have independently verified Master Control Loop/alert wiring, not suppressed warning flags.
- ACS-01..05 must pass fresh scheduled execution and independent report verification.
- No Slack, new payments or recurring healthy-status emails.
- Code review and test success do not constitute operational recovery.
