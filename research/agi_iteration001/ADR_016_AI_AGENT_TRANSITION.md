# ADR-016 — Transition Project AGI from deterministic role scripts to bounded AI-assisted research

Status: **PROPOSED, not deployed**. Date: 2026-11-19 Pacific. Target branch `research/agi-iteration-001-20261119`.

## Why this is needed

Milestone 15 established three deterministic Python software roles with immutable SQLite handoff receipts, 149 tests passing in GitHub Actions, and a reviewer that independently recomputes scores. The 55-agent registry contains 55 *proposed* roles with none production-enabled. This is software orchestration, not independent AI research, multi-agent intelligence, recursive learning, or AGI. Its training corpus is very small, hand-written, reused and not a scientific proof of generalization.

The research direction should **not** be reduced to adding more classifier gates or claiming a fleet is operational.

## OpenAI primary-source implementation guidance (verified November 2026)

- Agents SDK: https://openai.github.io/openai-agents-python/agents/ — model-based agents, runner, tools, handoffs.
- Orchestration: https://developers.openai.com/api/docs/guides/agents/orchestration — manager-as-tools vs explicit handoffs.
- Tool & human guardrails: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals — guardrails do not uniformly intercept handoffs; place checks at each action boundary.
- Tracing: https://openai.github.io/openai-agents-python/tracing/ — model calls, tools and handoffs traceable; avoid exposing credentials or private data.
- Agent evals: https://developers.openai.com/api/docs/guides/agent-evals — use workflow traces and independent grading.
- Evaluation best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices — evaluate tool choice, handoff logic, completion.
- Structured outputs: https://developers.openai.com/api/docs/guides/structured-outputs — schema-constrained typed agent proposals.
- Model optimization: https://developers.openai.com/api/docs/guides/model-optimization — evaluate before optimization; model training remains separate from agent orchestration.
- Billing separation: https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform — a ChatGPT subscription does not itself pay for or authorize API use.

## Boundaries and execution plan

1. Preserve current `three_role_research_cycle.py` as a tested **deterministic baseline**. Freeze its CI results and model checkpoint choices. Keep the production ACS system untouched.
2. Build an optional `proposal_provider` interface. The first version **must be an offline fake** that supplies recorded JSON proposals; tests run without network, tokens or API keys. An OpenAI model provider can be added only behind explicit enabled configuration, hard call/cost budgets, key provisioning, zero secrets in traces and approval.
3. Introduce typed proposal schema: `hypothesis`, `experiment_id`, `model_family`, enumerated bounded hyperparameters, `compute_budget`, `expected_falsifier`, `metric`, `dataset_ids`, `stop_conditions`. Reject invented results, arbitrary shell commands, import statements, external URLs, tool names, paths or deployment instructions as executable model actions. Interpret model outputs as untrusted data.
4. Planner AI generates competing proposals from permitted model families. Engineer executes **only allowlisted training specifications** in existing isolated CI resources; model output cannot directly write GitHub, access PythonAnywhere, run arbitrary code or purchase compute.
5. Evaluator re-runs experiments from frozen source+manifest, checks receipts and seed reproducibility, computes uncertainty, leakage, training cost and protected holdout results. A separate reviewer can critique proposals but cannot unilaterally promote them.
6. Promotion requires independent newly sourced labels, audited provenance/licensing, untouched test set, predetermined accuracy/robustness metric, clear gain vs baseline, no regression, and human approval for production. A failed experiment is an explicit negative result, not silently hidden.
7. Add event-level records for proposal, allowlist validation, training, metrics, evaluator decision, rejection reason, cost/call counters and SHA-256 artifact digests. Daily summary can be connected after verified safe operation and user opt-in; no unapproved emails/SMS/Slack.
8. Scale from three operational specialized AI-backed roles to more only when they demonstrate repeatable, useful improvements and bounded operational behavior. Targeting 55 agents is an aspiration, not a requirement for early progress.

## Acceptance tests

- Offline stubbed model proposer is able to propose at least two *different* allowed architecture configurations; both are exercised under the same compute budget and reproducible seeds.
- Malformed model output and prompt-injection-like instructions are rejected without code execution, credential exposure, production side effects or budget exceedance.
- Separate executor and evaluator independently produce identical metrics from frozen artifacts, and both results are recorded.
- CI intentionally fails when reviewer finds a tampered training receipt or a forbidden write.
- Workflows must verify the exact source commit rather than relying on a mutable branch alone.
- Recorded traces and logs redact sensitive inputs. Model providers remain **disabled by default**; no API charges.
- No AGI capability or autonomous self-improvement claim unless repeated independent benchmark evidence supports it.

## Immediate next engineering patch

Deliver `research/agi_iteration001/proposal_provider.py` with `OfflineProposalProvider` and a validated `ProposalSpec` data structure, with tests for malicious, malformed and out-of-budget proposals. Integrate it into a new research-cycle v2 while retaining the existing v1 as a baseline. Do not copy an LLM string into `exec`, `subprocess`, `shell` or an unrestricted Python import. Only train explicit allowlisted programs.

## Out-of-scope this iteration

No deployed AGI, no 55 active agents, no live AI model API access, no self-editing production code, no training large foundation models, no paid services, no changes to ACS-03/ACS-05. This ADR is an evidence-based proposal; it is not proof of execution.
