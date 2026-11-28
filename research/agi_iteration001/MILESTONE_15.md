# Milestone 15 — Three executing bounded research roles

The prior audit identified a serious gap: the 55 proposed agent entries were not 55 operational research agents, and the earlier worker proof mostly emitted checklists. This milestone introduces a **real three-stage execution loop**, with persisted, cryptographically identified handoffs and an independent recomputation check.

### What actually runs
1. **Research planner** emits a falsifiable hypothesis, bounded three-model architecture search and strict compute/sample budget.
2. **Model engineer** trains *three genuine research classifiers* (one Naive Bayes word baseline and two bounded character-n-gram variants) on the existing 18 training samples. It compares macro-F1 on the 12 validation examples and selects only when strictly better than baseline, with deterministic tie-breaking. The previously exposed test/confirmation data are not used for selection.
3. **Independent evaluator process role** independently rebuilds the three models, recomputes all validation scores, checks dependency receipt hashes, and reports results on an already-exposed confirmation set *only as descriptive evidence*. It blocks research promotion because there is no fresh independently sourced benchmark.

Each stage records an immutable SHA-256 receipt to SQLite; operations are dependency-gated, repeatable and fail on tampered stored output. CLI supports `init`, `planner`, `engineer`, `evaluator`, `run`, `status`. GitHub CI invokes the workflow on its own temporary filesystem and records the resulting JSON, including model scores and review block.

**Precise claim:** These are **three actually executing, deterministic software worker roles**, not three LLMs, independent reasoning agents, or a continuously running 55-agent fleet. No model architectural novelty beyond hand-coded candidate variants. Test data are small and reused; successful process orchestration is not evidence of AGI or independent scientific discovery.

### Run from research directory
```sh
python3 three_role_research_cycle.py --db ./local_research.db run
```
Do not point the database to production. No paid compute, credentials, production writes, scheduling, model promotion or unapproved agent spawning. Bounded compute and human review remain mandatory for substantial experiments.
