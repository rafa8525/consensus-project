# Milestone 15 — verified bounded three-role research cycle

GitHub Actions verification: https://github.com/rafa8525/consensus-project/actions/runs/44685839534  
Research commit tested: `62612437979e3302cf91aa5ed4ce31e66616771a`

**CI:** 149 tests passed. Registry checked: 55 unique proposed role definitions, none production enabled.

### Executed three-stage pipeline
1. `research_planner`: predeclared hypothesis; baseline plus two candidate configurations; budget capped at 3 model fits.
2. `model_engineer`: trained word NB baseline and two character-ngram variants on 18 hand-authored `TRAIN` examples. Selected by existing 12-example `VALIDATION` set, macro-F1 strictly better than baseline; deterministic tie break.
3. `independent_evaluator`: recomputed training and validation metrics, verified handoff SHA-256 receipts, and evaluated on an already exposed 18-example confirmation set for contextual review. Results saved as immutable per-role SQLite receipts. Rerunning preserves existing receipts.

| Model | Validation correct / 12 | Validation macro-F1 |
|---|---:|---:|
| Word-only NB | 6 | 0.481818 |
| Word+character 3-gram (alpha 0.5) | 9 | 0.742857 |
| Word+character 4-gram (alpha 1) | 9 | 0.742857 |

Selected character trigram n=3, alpha 0.5. Note these are repeated, previously used examples, **not an independent claim of improvement**.

Already-exposed 18-example confirmation after training on 18 `TRAIN` examples:
- Baseline: 12 correct, macro-F1 0.679365
- Selected candidate: 12 correct, macro-F1 0.670707

These results differ from some earlier milestones because their models were fitted on `TRAIN+VALIDATION` (30 examples); the current experiment correctly keeps validation out of training. They are not contradictory if the training splits are distinguished.

Evaluator output: `recomputed_validation_matches=true`, `independent_holdout_achieved=false`, `research_candidate_approved=false`, `production_changes=false`.

### Scope and limitations
- **Three operational deterministic software roles** that perform genuine, distinct actions and store durable task results; NOT three separate independent LLMs, not a 55-agent operational fleet, and not continuously scheduled.
- Planner alternatives are hand-coded; no generative architecture design or recursive autonomy yet.
- Evaluation corpus too small and previously exposed; no verified independent scientific generalization or AGI capability.
- CI uses temporary SQLite and deletes it after verifying persistence across separate CLI invocations; production cloud and PythonAnywhere unaffected.
- Next action: separate model-design proposal logic from orchestration, introduce falsifiable reasoning and planning tasks with a genuinely independent holdout, validate human-reviewed provenance, and fix CI checkout to pin exactly the evaluated commit.

**Decision:** execution pipeline proven; no model promotion and no change to production AI Consensus.
