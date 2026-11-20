# Milestone 20 — CI-verified bounded planning proposal experiment

**CI:** https://github.com/rafa8525/consensus-project/actions/runs/44788608019  
**Verified source commit:** `1ac769ccfb2ef6df303f847b7fe17c0f35f192a3`  
**Tests:** 212/212 passed. Branch remains isolated; zero role definitions production-enabled.

## Method

A structured proposal provider with a narrowly allowlisted heuristic family, tie-break policy, and weight generates three recorded proposals. The source was **authored by this AI assistant** and committed as code; this is not a live autonomous model proposer.

The deterministic grid generator is reused, with development seeds 20000–20031 (32) and internal test seeds 30000–30063 (64), excluding all exposed Milestone 19 seeds. An exact Dijkstra cost serves as reference. The selection objective was defined before executing CI: require all 32 development plans optimal; then minimize mean expanded nodes. There were 96 candidate-development search evaluations. Selection happened before opening test measurements.

## CI results

| Metric | Baseline Dijkstra | Candidate A (admissible min-edge Manhattan, high-g tie) | Candidate B (min-edge Manhattan *1.25, high-g tie) |
|---|---:|---:|---:|
| Development optimal plans | 32/32 | 32/32 | 32/32 |
| Development mean expansions | 117.094 | 113.844 | 112.750 |

**Selected: candidate B.**

| Test measure | Dijkstra | Selected B |
|---|---:|---:|
| Optimal 64-case plans | 64/64 | 64/64 |
| Mean expansions | 114.141 | 107.938 |
| Relative mean expansion reduction | — | ~5.43% |

These are node-expansion counts rather than end-to-end speed, CPU time, model compute efficiency or general intelligence. An inflated A* heuristic is not universally admissible; 64/64 cost matches on internally generated grids do not prove universal optimality. Test seeds are exposed after this run. Repeated runs are regressions, not fresh confirmation. The arithmetic reviewer recomputes results using the same implementation, rather than an independently developed oracle.

## Decision and next

**Engineering result:** validated experiment proposals selected a more search-efficient algorithm on this specified synthetic grid family.  
**Scientific result:** encouraging *narrow planning search efficiency*, not demonstrated independently generalizable learning improvement.  
**Deployment:** blocked; production changes false; model API calls 0; billed USD 0; trained ML models 0; 55 proposed agents remain non-production.

For the next milestone, move to distinct problem-generating families and an independent planner/evaluator implementation. Compare proposal providers with a truly equal compute budget and include difficult counterexamples. To test AI research autonomy, obtain approval for a controlled model-backed proposer with authenticated billing limits before issuing any live API request. Do not tune on M20 test seeds after exposure.
