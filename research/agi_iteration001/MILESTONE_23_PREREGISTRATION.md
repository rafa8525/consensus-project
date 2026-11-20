# Milestone 23 preregistration — bounded symbolic rule inference

**Status: frozen BEFORE benchmark implementation and first CI execution.**

### Objective

Demonstrate a task where a research executor genuinely **infers a per-task rule from examples** rather than only selecting a prewritten search heuristic. Compare a memorization baseline, affine modular rule inference, and an expanded two-family rule inducer with exactly the same demonstration/test examples. This is a small *symbolic program-synthesis task*, not foundation-model training or AGI.

### Benchmark and fixed design

- Each task supplies **8 distinct demonstrated input/output pairs** of integer inputs x,z in 0..10 and output y in 0..10.
- Each task's latent rule belongs to one of these programs: `(a*x+b*z+c) % 11`, `(a*x*x+b*z+c) % 11`, or `(a*x*z+b*z+c) % 11`, with coefficients a,b in 1..10 and c in 0..10.
- A seed is used only by the benchmark generator. Program proposers may access 8 demonstrations, **not the generator seed, coefficients, or withheld examples**.
- All 8 examples are drawn without replacement from 121 possible (x,z) pairs; there are 16 distinct query examples from the remaining pairs.
- Development: 12 tasks of each family, deterministic seed ranges 81000..81011, 82000..82011, 83000..83011. Evaluation: 20 tasks per family, seed ranges 91000..91019, 92000..92019, 93000..93019. Zero overlap. Total **36 development and 60 test tasks**, 960 withheld predictions.
- Baseline: retrieve known demonstrated output if exact input present, else output majority demonstrated label. No access to other benchmark tasks.
- Affine candidate: enumerate a,b,c for the affine family only. If no perfect match to all demos, abstain to majority fallback. Ties among consistent rules select lexicographically.
- Universal candidate: enumerate the same 1,100 program combinations for each of the three allowlisted feature families (affine, square x², interaction x*z), choose the least complex **fully consistent** hypothesis with the declared family order. No arbitrary code execution. If no candidate matches, use majority baseline.
- Global execution cap: maximum 4,000 program hypotheses tested per task per arm, and no API/network calls. Actual work per arm should be recorded, not misrepresented as equal CPU.
- Metrics: held-out exact prediction accuracy per family; number of consistent rules and program hypotheses evaluated; evaluate all three candidate policies on identical task identities.
- A deterministic development-only selector selects the highest withheld-development prediction accuracy with the lowest average hypothesis count as tie break (baseline wins ties).
- **Selection must occur before final test reporting**. Do not adjust code, family order, tasks, thresholds, or metrics in response to the test results.
- Independent evaluator: recomputes the held-out target from the generator's fixed latent coefficients, verifies each candidate's reported answer and maintains an immutable SHA-256 result digest. Because the generator and program classes are constructed here, this is an internal, not externally independent benchmark.
- Success means exact prediction accuracy improves over baseline on fresh, same-family generated tasks without unverified promotion. No AGI or autonomous model-discovery claim.

### Spend and deployment boundaries

No live LLM/API call, paid compute, ChatGPT support-site posting, ACS production changes, GitHub main merge, or 55-agent activation. The current optional OpenAI model proposal adapter is **still disabled**. Separate explicit authorization will be sought before real API calls or spending.
