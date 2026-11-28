# Milestone 21 — Cross-family robustness results

**GitHub Actions:** https://github.com/rafa8525/consensus-project/actions/runs/44789177293  
**Verified source revision:** `91101d14991fe9c49de8bf98bede67a681ad5415`  
**CI:** 223/223 tests passed. Registry audit: 55 proposed roles, zero production enabled.

## Protocol
Frozen Milestone 20 proposal, with three candidates:
- `baseline`: Dijkstra.
- `candidate_a`: minimum-edge-cost Manhattan A*, weight 1.0 (admissible), high-g tie break.
- `candidate_b`: previously selected minimum-edge-cost Manhattan A*, weight 1.25 (not universally admissible), high-g tie break.

Four generated 12×12 weighted grid families, each with 64 deterministic new seed instances (256 total): original-like, dense low-cost, sparse low-cost, cost-band. Route costs independently checked by a queue-relaxation Bellman–Ford-style oracle. Three candidates tested per case = 768 candidate evaluations; repeated tests are regression runs. These are **internally generated evaluations**, not externally sourced independent test data.

## Results

| Grid family | Baseline optimal | Candidate A optimal | Candidate B optimal | Baseline mean expansions | Candidate A mean expansions | Candidate B mean expansions |
|---|---:|---:|---:|---:|---:|---:|
| Original-like | 64/64 | 64/64 | 64/64 | 115.781 | 111.281 | 109.922 |
| Dense low-cost | 64/64 | 64/64 | 64/64 | 89.531 | 70.906 | 64.000 |
| Sparse low-cost | 64/64 | 64/64 | **52/64** | 134.406 | 95.984 | 52.031 |
| Cost bands | 64/64 | 64/64 | 64/64 | 128.062 | 125.609 | 124.703 |
| **Overall** | **256/256** | **256/256** | **244/256** | **116.945** | **100.945** | **87.664** |

All 12 failures of candidate B occurred in the sparse, low-cost family; observed maximal path-cost regret was 1. Example seeds and verified costs: 61000: 27 vs oracle 26; 61004: 28 vs 27; 61010: 25 vs 24.

Candidate A maintained exact optimal cost across 256 cases while averaging about **13.7% fewer expanded nodes** than Dijkstra. Candidate B required about 25.0% fewer expansions but violated exact optimality on 12 cases. These are counts of expanded nodes, not CPU time, training compute or general intelligence.

## Decision and consequences

- **Reject unconditional promotion of the previously selected candidate B.** Its tradeoff is potentially useful only where bounded suboptimality is explicitly acceptable, which is not the present objective.
- Candidate A is a sensible *hypothesis for a future preregistered trial*, not a newly confirmed independently heldout winner. Do not silently re-select or optimize on these now-exposed test cases.
- An isolated independent route-cost oracle helped uncover a failure that Milestone 20's original test sample missed.
- No new model trained; no live AI research agent; no API charges; no production changes; no evidence of recursive intelligence gain; the original 55 roles remain proposed only.

**Next:** pre-register fresh, more varied planning benchmark families, compare A vs Dijkstra with an independent oracle and stronger adversarial examples, and measure performance under fixed end-to-end runtime/CPU budgets. Separately run a truly model-backed proposal trial only with explicit billing authorization.
