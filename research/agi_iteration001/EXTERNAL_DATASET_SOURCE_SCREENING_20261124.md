# External dataset source screening — Project AGI
**Date:** 2026-11-24 (Pacific). **Status:** SOURCE REVIEW ONLY; zero external records downloaded or imported.

## Actual target task (do not change label semantics)
The current local classifier predicts one of exactly:
1. `design_experiment` — user requests a testable experiment, controls, procedures, design choices, ablations, or a trial plan.
2. `evaluate_evidence` — user requests measurement, statistical review, score/reliability/quality analysis, replication evidence, or scrutiny of observed outcomes.
3. `review_hypothesis` — user requests scrutiny of a causal claim, assumptions, alternative explanations, falsifiability, confounders, or rival hypotheses.

The input unit is an **instruction-like research task/request**, not an academic citation sentence, an evidence entailment pair, a news article, or a generic intent category. These distinctions matter more than the number of records available.

## Screened sources (not approved datasets)
| Source | Verified original task and rights information | Match to our three target labels | Verdict |
|---|---|---|---|
| AllenAI **SciCite** | Scientific citation intent classes `Method`, `Background`, `Result`; ~11K annotated citation contexts. Source repository `LICENSE` contains Apache-2.0 text, but do not assume every upstream scholarly citation is freely re-licensable or that the repository's license clearly covers third-party underlying text. Dataset card does not clearly specify a separate license. https://github.com/allenai/scicite ; https://github.com/allenai/scicite/blob/master/LICENSE ; https://huggingface.co/datasets/allenai/scicite | **No**. Method citation is not `design_experiment`; Background is not `review_hypothesis`; Result is not `evaluate_evidence`. | **Reject direct reuse**; inspiration only for provenance/annotation |
| AllenAI **SciFact** | Expert-authored claims and evidence verification. Publisher explicitly licenses `claims_*.jsonl` claims and evidence annotations under **CC BY 4.0**; `corpus.jsonl` abstracts from S2ORC under **ODC-By 1.0**; code under Apache-2.0. Do not conflate these rights. https://github.com/allenai/scifact/blob/master/LICENSE.md ; https://github.com/allenai/scifact ; https://huggingface.co/datasets/allenai/scifact | **No**. Evidence `SUPPORT/REFUTE` is an entailment label, not an instruction to evaluate evidence; corpus units differ. | **Reject direct evaluation**; potential *source-material pool* only if separate licensing, sampling and human re-annotation review are approved |
| **UserIntentBench** (JingmingChen) | Public dataset card describes structured, web-grounded user intent tasks and states its research-text/multimodal task records are **CC BY 4.0**. Its actual research tasks, license scope and provenance must be checked from an accessible canonical release: the complete dataset card was not directly retrievable during this screen. https://huggingface.co/datasets/JingmingChen/UserIntentBench | **Closer input format**, but has no verified gold labels for our three classes and would require licensed, independently blinded labeling; task contamination risk must be checked. | **Conditional review candidate, NOT approved** |
| **New independently created research-task prompt set** | Text drafted by independent human contributors with explicit written usage/release permission (e.g. contributor-approved CC BY 4.0), sourced independently of model training, prior tests and previous researcher examples; labeled blind by different humans. License does not exist until actually granted and recorded. | **Best direct semantic fit**, if independent prompt collection, consent and annotation safeguards are genuinely established. | **Recommended approach to prepare**; NOT yet collected, licensed, annotated, or certified |

## Methodology references (not dataset sources)
- Datasheets for Datasets (Gebru et al.), capture motivation, collection process, downstream uses, provenance and limitations: https://www.microsoft.com/en-us/research/publication/datasheets-for-datasets/
- Hugging Face Dataset Cards metadata includes license, language, size, bias, and permitted use: https://huggingface.co/docs/hub/datasets-cards
- Argilla / Hugging Face annotation guide: write guidelines first, multiple blind annotators and measure agreement: https://huggingface.co/docs/course/chapter10/4
- NIST AI RMF MEASURE: data quality, representativeness and independent validation considerations: https://airc.nist.gov/airmf-resources/playbook/measure/
- DOME recommendations for supervised ML emphasize independent evaluation, dataset provenance and documented license: https://www.nature.com/articles/s41592-021-01205-4

## License and provenance gate before ANY import
1. Identify exact rights holder, the *precise text subset* to reuse, license URL and version, and attribution/share requirements. A license on code does not automatically license every included research paper, abstract or derived sample.
2. Establish lawful permission for research evaluation **and for repository storage/redistribution** separately; if repository distribution is not permitted, no source texts may enter the GitHub repo.
3. Preserve canonical source URL, release/tag/version, retrieval date, file/content SHA-256, collector and annotator pseudonyms, original source document/record IDs where permitted, collection methodology, inclusion criteria, no private/secret data and consent.
4. Independently label our *actual* three classes. Never translate external labels to our labels by keyword, guessed mapping, LLM self-labeling or use of the model predictions as gold labels.
5. Check exact, normalized and near-duplicate overlap against training, validation, prior test, confirmation, stress and any other model-selection data. Group near-duplicates by originating source; reject contamination.
6. Keep evaluation labels and texts inaccessible to model selection/tuning; freeze baseline and candidate before measuring.
7. Have a human reviewer document provenance and labeling quality; existing `external_benchmark_gate.py` validates manifest **declarations**, not their truth. `independent_provenance_verified` must remain `false` until an evidence-backed review.

**Decision:** No existing screened dataset can be accepted as-is for this task. Prepare the independent prompt-collection and blinded-labeling protocol; request separate approval before importing third-party content, spending money, contacting annotators or changing production/workflows.
