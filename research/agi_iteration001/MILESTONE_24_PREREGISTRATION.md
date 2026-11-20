# Milestone 24 preregistration — frozen symbolic inference OOD check

Frozen before implementation and first CI observation.

**Purpose:** Establish whether the exact Milestone 23 three-family search policy can signal unsupported rules rather than confidently making unsupported predictions.

- Freeze the M23 search algorithm and the three existing feature families without modifications.
- Generate 30 in-language tasks (10 each: affine, square, interaction) and 30 out-of-language tasks (15 each: mixed square-plus-interaction `(a*x*x+b*x*z+c) % 11`, and nonlinear conditional `(a*x + b*z+c + 3*(x>=5))%11`). Coefficients sampled 1..10 for a,b, 0..10 for c. Use 8 unique demonstrations and 16 withheld queries per task.
- Fixed task seed ranges: in-language 110000–110009, 111000–111009, 112000–112009, OOD 120000–120014 and 121000–121014.
- No seed exposure from M23, no selection using OOD results, no changing policies after results. Generator is project-authored and not independently external.
- Candidate rule consistency with all 8 demonstrations is required for an **accept** decision; if none exists, **abstain** rather than returning the old majority-label fallback. Compare this abstaining policy against M23 forced fallback.
- Metrics: acceptance rate on known language, false accept rate on unsupported language, accuracy over all requested queries counting abstentions as incorrect for coverage-adjusted accuracy, conditional accuracy on accepted tasks, hypothesis evaluations. Full per-family breakdown required.
- This is NOT a guarantee of OOD detection. Finite evidence may allow an incorrect in-language expression to fit unsupported rules.
- No model promotion, API calls, keys, production changes, or autonomous agents. This benchmark assesses a narrow symbolic program-synthesis failure mode, not AGI.
