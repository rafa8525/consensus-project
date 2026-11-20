# Milestone 21 — Cross-family robustness and independent route-cost oracle

The Milestone 20 recorded proposal selected weighted A* with heuristic scaling 1.25 on a synthetic grid-distribution sample. Its 64/64 optimal-path matches cannot establish optimality in general.

This milestone **freezes** that candidate and evaluates it on four generator families (64 seeds each): original-like, sparse low-cost, dense low-cost, and cost-band grids. It compares the candidate, the original Dijkstra baseline and an admissible A* comparator against an independently implemented **queue-relaxation oracle**, which does not call the search algorithm's heap logic.

Record per-family exact-optimal counts, mean node expansions, maximum observed path regret, and a few counterexamples. No model selection, tuning or promotion is permitted after observing this evaluation. Subsequent reuse of the 256 cases is regression testing, *not* untouched confirmation. The generator was authored in this project, so independence refers to separate algorithm implementation, not an external scientific benchmark or independent human labels.

Both baseline and admissible A* should agree with the independently implemented oracle on nonnegative edge costs; the weighted A* version is not guaranteed to. If any failure appears, use it to diagnose robustness rather than tune against these cases.

All workers remain deterministic software; no AI models proposed new variants during execution, no general intelligence advancement is claimed, and there is no deployment or API spending.
