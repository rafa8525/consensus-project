# Review of the one-shot live API workflow — 2026-11-20

**Status: DRAFT ONLY. DO NOT ADD ENVIRONMENT SECRET YET. NOT INSTALLED ON MAIN. NO API SPEND.**

## GitHub platform limitation

GitHub's manual `workflow_dispatch` requires that the workflow definition already exist on the **default branch**. Our default is `main`, and the allowed environment deployment branch is `research/agi-iteration-001-20261119`. A workflow placed **only** on the research branch may not expose a runnable button. Source: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow

The candidate workflow is deliberately stored as **`research/agi_iteration001/LIVE_WORKFLOW_CANDIDATE.yml`**, outside `.github/workflows/`, meaning it is **not executable**. To enable it, a separate approved metadata-only change would copy this reviewed definition to `.github/workflows/agi-one-shot-live.yml` on default branch `main`; afterward, a manual run must select the restricted research branch. The user has not approved writing to main, so this change is a hard approval boundary.

## Security architecture

1. `workflow_dispatch` **only**, no push, pull_request, schedule or repository_dispatch, no automatically triggered paid tasks.
2. Explicit typed confirmation `YES-REVIEWED`; job checks repository, branch and first run attempt before touching the protected environment.
3. Environment `agi-research-live` configured with required reviewer `rafa8525`, admin bypass disabled, restricted to named research branch. User screenshots show this configuration; GitHub connector cannot independently read environment settings.
4. `permissions: contents: read` and `timeout-minutes: 4`. No production API, repository write, cloud auth or secrets passed to earlier jobs.
5. No reusable third-party checkout/install action in the paid job. Clone the public repository and check out an **immutable SHA** `10d829304ec11f4d036d8c882c2f24047f1922ad` containing the exact audited one-shot Python program. A later source edit cannot change this execution without a separately reviewed workflow update.
6. Environment secret named `OPENAI_API_KEY` and environment variable named `OPENAI_PROJECT_ID`; both exist **only once approved** and never in GitHub source, outputs or chat. Do not create repository-level secrets.
7. The Python adapter restricts model to `gpt-6-luna`, `max_output_tokens=800`, `store=False`, `tools=[]`, fixed system text, fixed small input and strict JSON schema, no model tools, no retries and one HTTP POST attempt per runner invocation. Raw content is never printed; only a SHA-256 hash of validated proposal is emitted.
8. Failure output generic, no raw exception printing (to limit leakage of request/response). The runner and GitHub do not verify external pricing or project credit limits automatically.
9. **Critically** GitHub environment review is per-run, not a cross-run lock. A new manual workflow dispatch could make another request if approved again. Revoking/removing the short-lived project-specific key immediately after the first run is necessary. Concurrent runs are serialized by `concurrency`, not guaranteed globally unique.
10. Public repository context: other workflows or users with branch write permission potentially can propose changes. The secret may be accessed by a workflow if the environment reviewer approves it. Review the exact code and workflow before granting each approval.

## Research scope and billing

Screenshots show `AGI Research Sandbox` project limit $1.00 with enforcement, allowed `gpt-6-luna` model only, $0.00 project usage, organization $10 prepaid credits with auto-reload off. These are **not up-to-the-second verified remote facts**. Billing enforcement may overshoot and does not offer an absolute $1 spend guarantee. A **single request** with short output usually costs far less than $1 at published rates, but tokens and actual billed usage must be checked separately after the call.

The existing model proposer is intentionally constrained to three familiar Naive Bayes variants; the initial test validates provider wiring and structured proposals, **not invention of new algorithms or general intelligence**. Successful model output cannot be executed as code. No 55-agent activation and no production changes.

## Before requesting user permission for default-branch workflow metadata

- [x] Draft stored in isolated research branch, with source pinned to reviewed code SHA.
- [x] Local tests exercise no-key rejection, wrong branch rejection, rerun rejection, mocked one successful request, invalid response and network failure no retry.
- [ ] Confirm CI test results for exact branch revision and secure lint of proposed workflow.
- [ ] Review GitHub environment setting screenshot after page refresh. (Evidence provided, though no connector admin read.)
- [ ] Review model price and current project allowance right before execution.
- [ ] Ask user **specific approval** to copy audited **metadata only** into `main`; do not merge other research files.
- [ ] After approved default-branch workflow exists, guide user to create environment-scoped secret and environment-scoped project ID variable. Never ask them to paste key here.
- [ ] In the GitHub UI, select research branch manually. User must approve the protected environment job and verify its code hash and allowed limits.
- [ ] Immediately retire the one-shot key after execution, review API usage, report only bounded trial outcome.

**Note:** This is a research workflow draft, not proof the live workflow can be dispatched. No user's payment authorization or API secret is present in the repository.
