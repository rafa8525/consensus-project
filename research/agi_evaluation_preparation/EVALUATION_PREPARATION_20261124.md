# Evaluation preparation — 2026-11-24
Draft only. Supplements research/agi_iteration001/INDEPENDENT_LABELING_PROTOCOL_DRAFT_20261124.md without replacing it. Parent reference a50a05da2424fb74175910447857eb8746322a86.
## Development pool
60 original assistant-authored requests, 20 intended per class, no reference labels. Development/calibration only: not independent human-authored data, not hidden, no external provenance or rights certification. Some requests refer to data not included and are suitable only for intent classification, not end-to-end execution. No training authorized. Exact normalized uniqueness checked within this pool; cross-corpus semantic overlap not verified.
## Independent labeling
Use existing labels design_experiment, evaluate_evidence, review_hypothesis; label principal action, flag ambiguity, do not force quotas. Two distinct authorized humans independently label fresh original human-authored items, blind to one another, predictions and target counts. Third distinct reviewer adjudicates disagreements and uncertainty with recorded reasons; exclude ambiguous items. Log pseudonymous IDs, rubric version, timestamps, rights and source evidence in restricted records. Proposed minimum 60 accepted items, 20 each class, raw agreement >=0.80 and Cohen kappa >=0.70 before adjudication. Do not fabricate votes. If gates fail, revise using development data and collect a fresh set.
## Hidden evaluation design
Future authorized independent custodian collects consented original prompts from contributors not exposed to training or development examples; exclude private or copied text and model paraphrases. Keep prompts, labels, votes outside agent-readable repository, memory and training. Before assessment freeze exact SHA-256, version, access log, provenance/rights, rubric, counts and exact/normalized/semantic overlap checks against prior corpora and source families. Custodian executes frozen models offline. Release only sanitized aggregates after approval, no item-level feedback to optimizer; retire exposed holdouts. No custodian, restricted store or holdout exists yet.
## Baseline comparison preregistration draft
Compare frozen existing word-only NB against frozen word+character NB (n=3, alpha=0.5), identical training data and label order. Pin code, training digest, Python and exact settings before accessing holdout; no tuning on holdout. Primary macro-F1; report accuracy, per-class precision/recall/F1, confusion matrices and paired correctness. Paired stratified bootstrap 95% CI of macro-F1 difference, 10000 replicates, seed 20261124; exact McNemar test secondary descriptive measure. Zero denominator metrics set to zero. Proposed research gate: positive lower CI bound for macro-F1 gain and no class recall loss >0.10; approve preregistration before evaluation. Otherwise inconclusive or regression. Small samples limit inference; classification gain is not AGI.
Separate future experiment: single-agent vs selective specialists vs all-55-role orchestration on same unseen end-to-end tasks, equal resource caps and tool/model versions, randomized order, blinded scoring, task completion, interventions, elapsed time, cost, safety violations. No agents actually executed here. Requires separate approval.
## Boundary
No outside recruitment, third-party corpus import, workflow dispatch, paid API requests, training, production changes or agent activation. Next authorization must identify independent contributor/labeler/custodian arrangement and rights-cleared restricted storage. No external data acquisition authorized.
## Development tasks (JSON)
```json
{
  "version": "2026-11-24-draft-v1",
  "status": "development_only_not_independent_not_hidden",
  "target_intent_counts": {
    "design_experiment": 20,
    "evaluate_evidence": 20,
    "review_hypothesis": 20
  },
  "tasks": [
    {
      "id": "DEV-001",
      "request": "Compare seedling growth with dawn versus dusk watering under matched conditions."
    },
    {
      "id": "DEV-002",
      "request": "Given battery lifetimes of 8, 10, 11 and 15 hours, summarize variation and limitations."
    },
    {
      "id": "DEV-003",
      "request": "Challenge the explanation that a quieter fan improved concentration when temperature also changed."
    },
    {
      "id": "DEV-004",
      "request": "Audit a claimed 20 percent defect reduction when production volumes differ."
    },
    {
      "id": "DEV-005",
      "request": "Identify assumptions behind attributing queues solely to checkout staff."
    },
    {
      "id": "DEV-006",
      "request": "Plan a controlled bicycle tire pressure trial for rolling resistance."
    },
    {
      "id": "DEV-007",
      "request": "Suggest rival explanations for increased orchard yield after fence installation."
    },
    {
      "id": "DEV-008",
      "request": "Devise a blinded taste test for three salt concentrations."
    },
    {
      "id": "DEV-009",
      "request": "Interpret a confusion matrix with high accuracy but poor rare-class detection."
    },
    {
      "id": "DEV-010",
      "request": "Specify random assignment and stopping rules for a reading-break study."
    },
    {
      "id": "DEV-011",
      "request": "Assess whether reported temperature differences exceed instrument resolution."
    },
    {
      "id": "DEV-012",
      "request": "Identify observations that would contradict a scheduling-rule explanation of fewer delays."
    },
    {
      "id": "DEV-013",
      "request": "Assess repeatability from six readings on the same reference object."
    },
    {
      "id": "DEV-014",
      "request": "Critique the proposed mechanism linking screen brightness to faster typing."
    },
    {
      "id": "DEV-015",
      "request": "Lay out a crossover comparison of two keyboard layouts controlling practice effects."
    },
    {
      "id": "DEV-016",
      "request": "Question whether packaging caused fewer returns when product mix changed."
    },
    {
      "id": "DEV-017",
      "request": "Choose matched conditions to compare insulation in identical containers."
    },
    {
      "id": "DEV-018",
      "request": "Explain how five withdrawals from a trial limit its reported estimate."
    },
    {
      "id": "DEV-019",
      "request": "Construct a factorial study of lighting and temperature on plant emergence."
    },
    {
      "id": "DEV-020",
      "request": "Compare median response times from two supplied logs and discuss outliers."
    },
    {
      "id": "DEV-021",
      "request": "Identify alternative causes of a fictional decline in network latency."
    },
    {
      "id": "DEV-022",
      "request": "Check whether a reported correlation survives removal of one extreme observation."
    },
    {
      "id": "DEV-023",
      "request": "Examine whether the claim that all improvements come from larger training sets is falsifiable."
    },
    {
      "id": "DEV-024",
      "request": "Design a fair comparison of route planners on a fixed road network."
    },
    {
      "id": "DEV-025",
      "request": "Find hidden assumptions in attributing team gains to adding a second reviewer."
    },
    {
      "id": "DEV-026",
      "request": "Prepare a pilot to test whether a checklist reduces assembly mistakes."
    },
    {
      "id": "DEV-027",
      "request": "Review measurements from three laboratories for systematic discrepancies."
    },
    {
      "id": "DEV-028",
      "request": "Set up a matched-pair test of two soil mixes with limited pots."
    },
    {
      "id": "DEV-029",
      "request": "Assess whether a reported uncertainty interval fits the number of observations."
    },
    {
      "id": "DEV-030",
      "request": "Challenge attribution of fewer missed turns to signs rather than traffic changes."
    },
    {
      "id": "DEV-031",
      "request": "Audit an aggregate benchmark score hiding failures in a small subgroup."
    },
    {
      "id": "DEV-032",
      "request": "Identify competing explanations for apparent soil moisture retention."
    },
    {
      "id": "DEV-033",
      "request": "Define controls and observation schedules for a sorting method trial."
    },
    {
      "id": "DEV-034",
      "request": "Critique the theory that one memory component explains every planning failure."
    },
    {
      "id": "DEV-035",
      "request": "Specify a procedure to test room noise effects on proofreading speed."
    },
    {
      "id": "DEV-036",
      "request": "Compare supplied successes and attempts using proportions rather than totals."
    },
    {
      "id": "DEV-037",
      "request": "Arrange a repeatable comparison of cache eviction policies on identical traces."
    },
    {
      "id": "DEV-038",
      "request": "Check a results table for inconsistent units and arithmetic errors."
    },
    {
      "id": "DEV-039",
      "request": "Describe evidence that would disconfirm clock drift as the cause of all scheduling errors."
    },
    {
      "id": "DEV-040",
      "request": "Interpret repeated sensor measurements in terms of precision."
    },
    {
      "id": "DEV-041",
      "request": "Question whether office layout and collaboration are linked by selection rather than causation."
    },
    {
      "id": "DEV-042",
      "request": "Plan a randomized comparison of two fictional reminder schedules."
    },
    {
      "id": "DEV-043",
      "request": "Identify rival explanations for apparent sensor improvement after recalibration."
    },
    {
      "id": "DEV-044",
      "request": "Design a test of container shape effects on cooling time."
    },
    {
      "id": "DEV-045",
      "request": "Assess two reported averages using their spread and sample sizes."
    },
    {
      "id": "DEV-046",
      "request": "Choose a sampling plan to compare inventory counting procedures."
    },
    {
      "id": "DEV-047",
      "request": "Check whether a delivery-time improvement survives removal of duplicate records."
    },
    {
      "id": "DEV-048",
      "request": "Examine assumptions behind claiming shorter tutorials cause better retention."
    },
    {
      "id": "DEV-049",
      "request": "Compare direction and magnitude of two independent replication estimates."
    },
    {
      "id": "DEV-050",
      "request": "Critique the claim that higher model confidence necessarily means greater accuracy."
    },
    {
      "id": "DEV-051",
      "request": "Outline a test matrix for humidity and packaging effects on paper curl."
    },
    {
      "id": "DEV-052",
      "request": "Identify a counterexample to the claim that adding specialists always improves decisions."
    },
    {
      "id": "DEV-053",
      "request": "Create a protocol comparing map legends on equivalent navigation tasks."
    },
    {
      "id": "DEV-054",
      "request": "Interpret observed false-positive and false-negative counts for two rules."
    },
    {
      "id": "DEV-055",
      "request": "Isolate the contribution of a preprocessing step in a classification experiment."
    },
    {
      "id": "DEV-056",
      "request": "Check a fictional results table for discrepancies between totals and percentages."
    },
    {
      "id": "DEV-057",
      "request": "Assess whether a proposed energy-saving explanation ignores ambient conditions."
    },
    {
      "id": "DEV-058",
      "request": "Assess confidence in a performance estimate based on three recorded runs."
    },
    {
      "id": "DEV-059",
      "request": "Challenge the assumption that success on familiar puzzles implies general reasoning ability."
    },
    {
      "id": "DEV-060",
      "request": "Propose a controlled test of practice intervals on puzzle completion."
    }
  ]
}
```
