# Milestone 22 — Verified preregistered confirmation results

**Preregistration (before evaluation):** `MILESTONE_22_PREREGISTRATION.md`, commit `4ea721059d13f7803699cd7a52fa84135969ea0c`.  
**CI verified code commit:** `052170111a756103c7887e54b9a17e699f295f8b`.  
**Successful GitHub Actions:** https://github.com/rafa8525/consensus-project/actions/runs/44799592372  
**Tests:** 234/234 pass, research role registry 55 proposed, zero production-enabled.

## Frozen trial
Compare M21 admissible A* (weight=1.0, minimum positive cell-cost Manhattan heuristic, high-g tie breaking) against Dijkstra on 4 different new generated 12×12 grid families, 48 seeded problems each (192 total). Use independent M21 queue-relaxation oracle to verify route costs. Candidate specifications and objective were committed before first results. No post-hoc candidate selection or tuning. Families: zigzag corridor, concentric cost, lane barriers, bimodal sparse. New deterministic seed range 73000–73047.

## Verified findings

| Family | Dijkstra optimal | Admissible A* optimal | Dijkstra average expansions | A* average expansions | Reduction |
|---|---:|---:|---:|---:|---:|
| Zigzag corridor | 48/48 | 48/48 | 112.354 | 108.479 | 3.449% |
| Concentric costs | 48/48 | 48/48 | 110.792 | 68.729 | 37.965% |
| Lane barriers | 48/48 | 48/48 | 79.333 | 70.500 | 11.134% |
| Bimodal sparse | 48/48 | 48/48 | 119.250 | 76.812 | 35.587% |
| **Overall** | **192/192** | **192/192** | **105.432** | **81.130** | **~23.1%** |

The preregistered primary exact-cost-correctness gate passed. All cases are now exposed; do not reuse them as an untouched holdout. The average relative gain uses pooled expanded nodes, not end-to-end runtime.

### Exploratory latency

Median single-call latency on one GitHub-hosted CI runner, from three alternating-repeat measurements per grid:

| Family | Dijkstra median nanoseconds | Admissible A* median nanoseconds |
|---|---:|---:|
| Zigzag corridor | 158,865 | 173,037 |
| Concentric costs | 182,171 | 132,241 |
| Lane barriers | 119,719 | 112,454 |
| Bimodal sparse | 195,122 | 152,250 |

Noise, CPU scheduling, and implementation-specific overhead mean latency is descriptive, not an acceptance criterion. In particular, A* was slower on the zigzag-corridor family despite expanding fewer nodes.

## Scientific interpretation and next research action

This is **independent algorithm verification within internally developed synthetic task families**, not an externally protected benchmark. The evaluator's oracle implementation is independent of the candidate's heap logic but shares this project and its generator assumptions. It supports the narrow claim that the admissible candidate is robust in these 192 cases and used fewer node expansions. It is also expected theoretically to preserve optimality with a consistent admissible heuristic on these positive weighted grids.

The benchmark does **not** measure actual AI-generated research hypotheses, model invention, neural training, language reasoning, or recursive self-improvement. The 55 proposed registry roles are not running autonomous researchers. No OpenAI API requests, charges, model promotions, production deployments, or ACS changes.

**Next:** obtain a genuinely independent model-research benchmark (or independent sealed dataset) with new task families and a blinded evaluation service, and compare a genuinely model-backed proposal agent against a deterministic baseline using matched *total* compute/call budgets. Activation of a live model still requires explicit model/cost authorization and independently controlled API billing. Prioritize meaningful AI-research capability over additional tiny engineering gates.
