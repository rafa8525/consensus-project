# Milestone 22 — Preregistered robustness confirmation protocol

Status: **FROZEN BEFORE FIRST EVALUATION RUN**. Research-only; no live models or production.

## Hypothesis
The previously identified admissible candidate A from M21 (minimum-cell-cost Manhattan heuristic, weight 1.0, high-g tie breaker) has **zero shortest-path optimality errors** on new structurally different 12×12 positive-weight grids and reduces average node expansions relative to the Dijkstra baseline. Unlike the weighted (1.25) variant, the admissible heuristic is a sound correctness-first candidate.

## Frozen comparison / allowed candidate implementations
- Baseline spec: `{'id':'baseline','heuristic':'dijkstra','weight':1.0,'tie_break':'low_g'}`.
- Candidate spec: `{'id':'candidate_a','heuristic':'min_edge_manhattan','weight':1.0,'tie_break':'high_g'}`.
- Do **not** select or tune using evaluation results. Evaluate these exact two specs only.
- Independently coded oracle: existing queue-relaxation shortest path from M21, already checked against baseline.
- Fixed random seeds: 73000–73047 (48) for each of four new families. These seeds do not overlap M19–M21.
- New families: zigzag corridor barriers with gaps; concentric rings of higher traversing costs; low-cost horizontal lanes with intermittent barriers; sparse obstacles with bimodal (1 vs 12) costs. Always guarantee the top+right perimeter path.
- 192 total grids; 384 candidate searches plus oracle runs. No optimization search or agent-generated proposal during evaluation.
- Primary criterion: **192/192 exact shortest paths** for candidate A, compared with separately computed oracle; if even one failure, correctness criterion fails.
- Secondary metric: mean node expansions per grid, reported by family and pooled, with absolute/relative difference; no claim if gains are absent.
- Exploratory metric: repeated paired `perf_counter_ns` solver-call latency in the same process, fixed iteration count and alternating method order. Timings are platform-sensitive and not stable CI acceptance criteria.
- All evaluation outputs include per-family digest and failure examples; results become **exposed** after first CI.
- Tests must include independent oracle agreement, tampered-spec rejection, deterministic summary, case-count and holdout seed exclusion.

## Governance / evidence standard
- Code and tests shall be committed to isolated `research/agi-iteration-001-20261119`; existing experiment source remains unchanged.
- No live OpenAI API calls, no new agent activation, no ML training or production deployment.
- This evaluation is **not a protected benchmark against a developer who controls both code and generator**, nor an external real-world reasoning benchmark. The assistant writing the benchmark also knows the candidate; claims must be limited to this generated family.
- Post-hoc analysis of failures may inform *future* preregistered experiments but cannot retroactively redefine success.
- A positive result means bounded shortest-path-search engineering gains only, **not** AGI or recursive improvement.

## Separate live AI research gate
The optional Responses adapter and mock admission ledger remain inactive. Authentication, independently enforced API cost controls, credentials and permission for actual charges are not in scope and should not be inferred from requests to continue research.
