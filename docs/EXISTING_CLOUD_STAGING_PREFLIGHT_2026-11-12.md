# Existing-cloud staging authorization and access preflight

2026-11-12. The owner authorized **isolated synthetic staging on an existing
environment only**, with **no production changes** and **no new paid resources**.
This is authorization to investigate and run a safe existing-resource staging
test *if permissions and costs can be verified*, not blanket permission to
touch the running ACS instances.

## Actual tool access observed

- GitHub repository `rafa8525/consensus-project`: connected; can read and
  commit to the isolated `phase2-5-system-demo` development branch.
- GitHub Actions: the isolated staging acceptance workflow has already passed.
- Google Cloud Compute Engine: no installed direct VM/IAM/SSH execution
  connector was available in this chat at the time of inspection.
- PythonAnywhere: no direct authenticated remote runtime or scheduled-task
  management connector was available in this chat at the time of inspection.
- The plugin directory search found no connected GCP/Compute Engine controller
  capable of verifying existing VM access rights here.
- Therefore remote VM **IAM permission verification, cost verification, and
  on-host isolation inspection are NOT complete**. No cloud deployment or
  host changes were attempted.

## Non-negotiable pre-deployment checks (on the intended existing host)
1. Identify exact pre-existing resource and billing project; confirm no new
   VM, address, disk, storage bucket, bandwidth service or chargeable feature.
2. Read current IAM policy and determine the least-privileged identity needed.
3. Audit existing ACS processes, owners, cron/scheduler, environment variables,
   filesystem mount points, storage capacity and logs *read-only*.
4. Establish separate sandbox OS user, dedicated temporary data directory and
   file permissions; no access to production credentials or data.
5. Disable external network egress for the synthetic runtime, if isolation can
   be guaranteed without affecting production traffic.
6. Execute only the previously green simulated test suite from a pinned commit
   in the sandbox, and record external process-level exit codes and timestamps.
7. Run read-only evidence inspection, then remove only sandbox-created files
   and processes. No changes to production scheduler or running agents.
8. Stop immediately on any unexpected billing exposure, permissions ambiguity,
   resource pressure, or evidence that the sandbox shares writable production
   state.

## Gate
Until an authenticated Compute Engine or PythonAnywhere connection provides
actual inspection and execution permission, **CLOUD_STAGING_BLOCKED**.
Do not turn green GitHub CI into a claim that GCP/PythonAnywhere staging ran.
