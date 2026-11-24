# Independent annotation and provenance protocol — REVIEW DRAFT
**Date:** 2026-11-24 Pacific. **Stage:** preparation only; **NO data collected, imported, licensed, labeled, or independently verified**.

## Research question
On research-task requests **independent** from our tiny existing local training/validation corpus, does the **frozen** word+character Naive Bayes model (`n=3, alpha=0.5`) outperform the **frozen** word-only Naive Bayes baseline on macro-F1 without unacceptable class-specific regressions?

## Proposed collection (not started)
- **Target:** 60 or more independently authored short English task requests, with a balanced reviewed gold standard of at least **20 per class**. This exceeds the existing intake code's minimum 30/8 per class. Target is a *proposal*, not a fact about any existing dataset.
- **Source:** independent human prompt contributors who have not copied or adapted examples from `local_inference.py`, `model_improvement_experiment.py`, prior holdouts or this project's CI. Each contributor grants explicit, recorded rights for the chosen use. No compensation or solicitation authorized by this draft.
- Collect research task instructions, not researchers' private data, personal records, licensed paper abstracts or model-generated paraphrases. Do not collect email addresses in the dataset; use pseudonymous participant IDs.
- Freeze source and collection rules **before seeing classifier predictions**. Record exact timestamps, source version, independent author IDs and consent/rights reference. Collect without looking at baseline/model predictions or validation-derived keywords.

## Label rubric (apply to the principal requested action)
- **design_experiment**: asks to formulate a test procedure, control, trial, comparison plan, experimental variables or resource-constrained design. Examples of decision cues: *design a comparison*, *set up a control group*, *plan an ablation*.
- **evaluate_evidence**: asks to audit observed measurements, check reported results, analyze quantitative/statistical evidence, estimate repeatability or validate a study's evidence. Decision cues: *inspect measured accuracy*, *assess error bars*, *verify benchmark reproducibility*.
- **review_hypothesis**: asks to challenge a proposed explanation or causal thesis, examine rival hypotheses, missing assumptions, confounders or falsifiability. Decision cues: *find alternate explanations*, *critique causal assumption*, *identify falsification condition*.

**Disambiguation:** Prefer the main verb/object, not superficial words such as “experiment”, “evidence”, “claim” alone. If multiple intentions are equally central, tag for independent adjudication; do not force a label merely to meet per-class quotas. Exclude unclear or mixed tasks rather than silently relabeling them. Do not reveal model predictions or training terms to annotators.

## Proposed human labeling workflow
1. An independent text contributor produces/authorizes an original prompt; record its source/license/consent before collecting it.
2. **Two different annotators** independently label every prompt using exactly the rubric above. Neither sees the model's prediction, the other's choice, or previous experiment results. Record pseudonymous annotator IDs, guideline version and two separate raw decisions outside the public CI repository.
3. Produce a pre-adjudication confusion matrix and both raw agreement proportion and **Cohen's kappa** (two annotators, three nominal labels). These summarize consistency, not ground-truth accuracy.
4. An independent third reviewer adjudicates all disagreements and uncertain labels with documented reasoning. Reject ambiguous multi-intent items instead of manufacturing certainty.
5. **Proposed quality gate:** >= 0.80 raw agreement and >= 0.70 kappa **before adjudication**; at least 20 distinct adjudicated examples in each class; all entries have traceable rights and independent origin. Thresholds are proposed governance policy, not recognized universal guarantees. If unmet, revise rubric and recollect **a different fresh set**; do not relabel the locked holdout until the measured score looks good.
6. Check exact and normalized overlap, plus near-duplicate semantic overlap and source-family sharing with all prior training/validation/test/confirmation/stress examples. Existing `external_benchmark_gate.py` covers exact normalized matches only, so an additional reviewed near-duplicate screening procedure is required before acceptance.
7. Freeze a signed dataset card/manifest and SHA-256 before first model assessment. Holdout rows must not be fed to any candidate tuning, prompt construction, or a new API experiment.
8. Compare only **frozen** word NB and 3-gram alpha=0.5 models on this external locked corpus. Report accuracy, macro-F1, all per-class precision/recall/F1, paired correctness gains and confidence interval; disclose small sample uncertainty and source limitations. Compare with old internal results **separately**.
9. Keep `promotion_approved=false`, `production_changes=false`, `independent_provenance_verified=false` until an authorized reviewer explicitly certifies independent rights/provenance and then separately approves any promotion.

## Required documentation before intake
| Field | Evidence needed |
|---|---|
| `dataset_id` / version | unique ID, timestamp and immutable release identifier |
| `source_url` | canonical creator/repository or private contributor consent record (not a fictional public URL) |
| Rights | rights holder, content-specific license, allowed evaluation/storage/distribution; attribution file |
| `sha256` | exact content digest after data is frozen, not placeholder |
| `collection_method` | actual method, timeframe, exclusions and source independence |
| `annotator_id` | pseudonymous reviewer ID for provenance manifest; separate audit log for every vote |
| `heldout_for` | `research-task-classification-v1` |
| Annotation | rubric version, raw double-blind labels, third-party adjudication decisions, agreement and kappa |
| Quality | 3 class counts, no duplicates, near-duplicate analysis, class-specific error review |
| Separation | attestation that no reference text was used to tune candidate or construct prompts |

## Explicit gates and restrictions
**Preparation APPROVED:** source/legal research, comparison matrix, rubric, manifest design, quality thresholds and no-data documentation on the isolated research branch.

**NOT APPROVED:** import/download of a third-party corpus into repository, text scraping/bulk collection, consent solicitation, payment to annotators, new external accounts, new secrets, API calls, automatic workflow dispatch, production changes, promotion/activation of any agent.

**Next decision:** approve **a specific source, content license and independent collection/labeling method** before beginning real dataset acquisition. When permission or quality cannot be established, default to rejection, not optimistic relabeling.

## Authoritative background
- https://github.com/allenai/scifact/blob/master/LICENSE.md — distinct claim/evidence vs abstract vs code licenses.
- https://github.com/allenai/scicite/blob/master/LICENSE — Apache-2.0 repository; independent underlying publication-text rights require care.
- https://huggingface.co/docs/hub/datasets-cards — license/provenance/limitations card convention.
- https://huggingface.co/docs/course/chapter10/4 — annotation guidelines and multiple annotations.
- https://www.microsoft.com/en-us/research/publication/datasheets-for-datasets/ — dataset provenance questions.
- https://airc.nist.gov/airmf-resources/playbook/measure/ — measured evaluation of data quality, representativeness, external validity.
