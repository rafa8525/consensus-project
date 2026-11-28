# Milestone 19 — CI-verified single-worker versus three-role planning benchmark

**GitHub Actions:** https://github.com/rafa8525/consensus-project/actions/runs/44689982454  
**Exact verified source revision:** `6ba6f7934edf567b75ab053847348d97086d72ee`  
**CI:** 200/200 passing tests; 55 role definitions proposed, zero production-enabled.

## Experimental protocol
A reproducible 12×12 weighted obstacle-grid shortest path benchmark uses three fixed candidate algorithms: Dijkstra, Manhattan A*, weighted Manhattan A* (1.5). Independent Dijkstra runs provide the optimal-cost oracle. Development seeds 1000–1023 (24 problems) and held-out, initially unexamined internal seeds 9000–9063 (64 problems) have zero overlap. Every candidate evaluated on the same 24 development problems; selection requires no deviations from optimal cost there, then minimizes mean node expansions. Both arms receive an identical predefined candidate set, train/evaluate no LLMs, and use the same development/holdout problem identities.

One deterministic worker selects directly. A three-role deterministic team plans, executes and independently recomputes development evidence. The team pays for **72 additional development candidate evaluations**; thus **total compute is not equal**, although candidate proposal/development/holdout budgets match before the team review overhead.

## Measurements

| Measure | Solo | Three-role |
|---|---:|---:|
| Selected proposal | weighted A* 1.5 | weighted A* 1.5 |
| Selected method development optimal | 24/24 | 24/24 |
| Held-out internal test optimal | 64/64 | 64/64 |
| Mean held-out node expansions | 107.938 | 107.938 |
| Extra development re-evaluations | 0 | 72 |
| Selection difference | none | none |

Other development candidates:
- Dijkstra: optimal 24/24, mean expansions 115.167.
- Manhattan A*: optimal 24/24, mean expansions 111.042.
- Weighted A* 1.5: optimal 24/24, mean expansions 107.125.

The same 64/64 heldout cost matches should NOT be interpreted as proof that weighted A* is universally optimal: its inflated heuristic is not generally admissible and counterexamples can exist. These 64 internal cases are now exposed for future work, not a fresh independent confirmation split.

## Conclusion

**No measurable collaboration advantage in this experiment.** Both arms used the same hard-coded proposals, so this design primarily measures workflow reproducibility and overhead—not whether AI-generated specialist ideas can outperform a solo research agent. The additional review work might detect tampered results, but this trial did not quantify that separate reliability benefit.

The algorithmic planning benchmark is more substantive than the prior intent-classifier exercises, yet it remains fully deterministic. It does not involve live AI models, independent architecture invention, recursive improvement, external ground truth or a working 55-agent collective. **Research promotion: blocked. Production changes: none. API cost: zero.**

## Next stronger experiment

Use a separate source of planning/program-synthesis tasks or externally reviewed benchmark. Introduce actual AI-backed but allowlisted proposals only after budgeting and explicit API authorization. Compare independent solo and team-generated proposals under **equal total** compute/token budgets, randomize seeds, preregister metrics, and evaluate fresh heldout task families. Record reviewer error detection as an independent metric; do not simply inflate the agent count.
