# Milestone 19 — Controlled solo-versus-three-role planning benchmark

## Hypothesis
A three-stage planner / engineer / evaluator workflow may improve output correctness or reliability over a single worker on a **bounded shortest-path planning task**. Falsifier: no outcome difference despite extra collaboration overhead.

## Protocol
- Generate reproducible 12x12 weighted grids with blocked cells and a guaranteed path, using Python's seeded PRNG. All edge costs are positive integers.
- Oracle: Dijkstra shortest path. Candidate algorithms: Dijkstra, admissible Manhattan A*, and weighted 1.5 Manhattan A* (which can be suboptimal).
- Development seeds 1000..1023 (24 instances), separate internal test seeds 9000..9063 (64 instances).
- Every candidate is evaluated only on development instances for selection. Require exact optimality on all 24 development instances; among eligible candidates prefer minimum average node expansions and deterministic tie-break.
- Compare one deterministic solo worker selecting from the same three algorithms with a three-stage deterministic team. Both receive identical candidate pool and evaluation sets. Team independently recomputes all development results, using **72 additional candidate searches**; this overhead is explicitly reported. The selected candidate is then measured on identical 64 internal test grids.
- Report per-arm optimality, mean expansions, seed hashes, selected candidate, extra evaluation overhead, and mismatches.

## Validity
This is a meaningful algorithmic planning *software* benchmark, but **it does not use AI-backed agents or novel AI-generated hypotheses**. The problem instances are programmatically generated and not externally sourced, and we have looked at the algorithms in advance. This does not show independent generalization, recursive model development, or AGI. If the arms match, report that result openly; it rules out claims of superior collaboration on this experiment.

The test split can no longer count as untouched after first CI run. Do not tune methods against it and then call it a fresh independent holdout. No external services, API tokens, production changes, role promotions, or spending. CI may run the deterministic benchmark repeatedly for regression checks only.
