# ACS backup candidate: deployment safety gates

This is a **staged candidate**, not the active ACS backup pipeline. Do not
merge or schedule until every gate below is verified.

## Included data and privacy

- Explicit sources: `memory/agents`, `memory/state`, `memory/knowledge`,
  `memory/consensus`, `registry`, and `memory/centralized_knowledge_base.txt`.
- The allowlist does **not** imply these files contain no credentials or
  personally identifiable information. Automated pattern checks catch only
  common credential forms. Review the intended content and retention policy
  before transferring data off-machine.
- No keys, credentials, API responses with secrets, or plaintext backup
  contents may be committed to GitHub.
- The current candidate does **not** cover all configuration and application
  artifacts needed for bare-machine disaster recovery.

## Encryption-key recovery (must be completed before any cloud backup)

1. Generate an independent random 32-byte AES-256 key outside the repository
   and outside cloud backup archives (permissions 0600, parent directory 0700).
2. Preserve an **offline, access-controlled recovery copy** of the key in a
   separate location. Never include the key alongside ciphertext backups.
3. Prove a fresh isolated recovery environment can obtain that copy and
   decrypt a synthetic backup before enabling production uploads.
4. Record key identifier/version metadata without publishing the key.
5. Define rotation/recovery and loss procedures. Without the key, encrypted
   backups cannot be recovered.

## Release checklist

- [ ] Candidate unit and integration tests pass on the PR's final commit.
- [ ] Privacy review covers both filenames and contents.
- [ ] Confirm actual Drive destination, API principal, access scope, quota,
      retention policy, and permissions using non-sensitive metadata.
- [ ] Verify service-account authorization with a harmless **encrypted
      synthetic** artifact only.
- [ ] Confirm uploaded metadata (size and MD5) and independently download,
      authenticate, and validate the same encrypted artifact.
- [ ] Confirm offline recovery key works in an isolated recovery test.
- [ ] Test restore completeness against a documented set of essential ACS
      functions; archive integrity alone is not sufficient.
- [ ] Implement a signed or otherwise trusted persistent backup-success record
      with timestamp, remote ID, encrypted SHA-256, and restore verification.
- [ ] Integrate failure and freshness evaluation with ACS-01 and test stale,
      missing, failed, and delayed jobs without disabling unrelated tasks.
- [ ] Confirm no duplicate scheduled backups; preserve the existing ACS-03
      fitness backup.
- [ ] Confirm zero-cost quotas and retention, and use conservative backups.
- [ ] Only then approve merge and controlled rollout with rollback plan.

## Operational cautions

- The Google Cloud Storage CRC32c email does not cover this Google Drive API
  integration. The prototype uses AES-GCM authentication and ZIP SHA-256
  manifest validation; Drive MD5 is an additional transport metadata check.
- No retention/deletion actions, live uploads, schedule mutations, or merges
  are wired into the candidate.
- Leave `tools/pa_tasks_audit.py` unexecuted: it contains task-disabling code.
