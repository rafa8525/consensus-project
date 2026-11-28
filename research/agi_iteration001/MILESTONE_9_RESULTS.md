# Milestone 9 — independently verified evaluation results

**CI evidence:** https://github.com/rafa8525/consensus-project/actions/runs/44679325402

**Verified commit:** `10c71f4077dde85cf20670a60057836860e64b2a`  
**CI:** 94/94 tests passed; agent-registry validator PASS (55 unique proposed, none production enabled).

- Train/development: 30 hand-authored items, 10 per task category
- Replicated CV: 5 stratified folds x 5 fixed random seeds = 25 correlated fold results
- Confirmation: 18 new hand-authored items, 6 per category, disjoint exact texts
- Candidate: word + character trigram NB, `n=3, alpha=0.5`, selected in Milestone 8
- Baseline: original word-only multinomial NB

| Metric | Baseline | Candidate |
|---|---:|---:|
| Mean cross-validation macro-F1 | 0.666222 | 0.756889 |
| Confirmation accuracy | 12/18 (66.67%) | 17/18 (94.44%) |

CV macro-F1 difference: +0.090667. Confirmation accuracy difference: +5/18 (+27.78 points).

**Paired bootstrap 95% percentile interval for accuracy difference:** [0.0, 0.555556]. The lower bound includes zero, so the predeclared replication gate failed. `replication_gate_passed=false`; `promotion_approved=false`.

**Interpretation:** Better measured scores on the current small, internally written corpus. No verified independent-source generalization, foundation-model capability, or AGI. No model checkpoint replacement, deployment, autoscheduler, external compute allocation or production modifications.

**Next research step:** Obtain genuinely independent labeled task examples, ideally curated and reviewed by separate sources or evaluators with provenance and licensing. Freeze the evaluation manifest and SHA before running candidates. Avoid test set reuse. Add timing/memory measurements and stronger capability benchmarks; distinguish classification tasks from reasoning and model-architecture invention.
