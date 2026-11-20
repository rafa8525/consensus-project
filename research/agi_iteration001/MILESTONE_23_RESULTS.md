# Milestone 23 — Verified bounded symbolic rule induction

**Preregistered design:** `MILESTONE_23_PREREGISTRATION.md`, committed as `a4980419a0f1f5e26d042cbf4f2837b3ce18ff1c`; corrected pre-run enumeration count by `5c8212cb8b0a5bd0d82f3c735344b1ef637915c8`.  
**Verified test revision:** `ab58ad1e69ef48f5c4fb66f0caec2efa51b014ec`.  
**CI:** https://github.com/rafa8525/consensus-project/actions/runs/44800556190 — 247/247 automated tests pass; 55 proposed roles, zero production enabled.

## Procedure

36 development tasks and 60 fresh seeded evaluation tasks, split across affine, x-square and x-z interaction modular programs. Each task provides 8 input-output demonstrations and 16 disjoint withheld queries; evaluations encompass 960 predictions. All algorithms receive identical examples. Baseline predicts the most frequent demonstration label; affine-only enumerates 1,100 possible parameter triples; broad search allows three predeclared feature families, up to 3,300 hypotheses. No learned LLM, neural parameters, external API or new executable expressions.

Selection was made using development only. The expanded three-family search was selected before test calculations.

## CI results

| Policy | Development correct / 576 | Test correct / 960 | Test hypotheses checked |
|---|---:|---:|---:|
| Majority label | 37 / 576 | **81 / 960** | 0 |
| Affine-only search | 220 / 576 | **378 / 960** | 54,726 |
| Three-family rule search | 576 / 576 | **960 / 960** | 100,989 |

Test breakdown for the winning policy: affine 320/320, square 320/320, interaction 320/320. Both other policies fail outside their limited representation. The expanded policy uses substantially greater compute than majority; do **not** describe this as an equal-compute comparison. It is an exact enumerative program synthesizer on deliberately known program families. The results are expected when every hidden rule is contained within the candidate DSL and eight examples suffice to identify a matching expression.

## Validity and next action

This verifies **per-task compositional symbol-rule inference within an explicitly known DSL**; a useful software capability but not demonstrated unknown-domain transfer, autonomous model improvement or foundation-model AGI. The 60 evaluation tasks are now exposed and cannot be reused as pristine independent tests. No external benchmark and no genuinely model-backed proposal agent were involved.

Next meaningful action: test deliberately out-of-DSL rules without changing the synthesizer and report errors honestly. Then stop at the genuine user-approval boundary for a bounded *live* AI model-backed proposal evaluation, with a real API credential, selected model and spending controls. No production writes, API billing, promotion, or 55-agent activation.
