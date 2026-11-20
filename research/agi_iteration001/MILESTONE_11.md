# AGI Milestone 11 — Independent-source benchmark integration (OOD only)

## Source investigated
CLINC150 (Larson et al., EMNLP 2019), published and archived by UCI:
- https://archive.ics.uci.edu/dataset/570/clinc150 (UCI reports CC BY 4.0; attribution required)
- https://github.com/clinc/oos-eval (original authors, repository terms should be checked separately)
- https://aclanthology.org/D19-1131/

CLINC150 provides 150 in-domain intent classes plus out-of-scope queries. It was crowdsourced independently of this project. **Its 150 classes cannot be mapped automatically into** `design_experiment`, `evaluate_evidence`, and `review_hypothesis`; the CLINC150 `oos_test` category is relative to CLINC's domains and is not a certified label for this project. Do not claim accuracy or improve research-task model ranking using those labels.

## Delivered
`clinc_ood_protocol.py` implements an offline, checksum-locked external-data reader for the original CLINC150 JSON structure. It uses only `oos_test`, validates row format, deduplicates and selects a stable max-200 text subset, and compares both frozen research models using a **predeclared lexical-coverage abstention threshold** (0.25). The output separates confirmation-set coverage from OOS false acceptance and **never approves model promotion**.

CI tests use synthetic fixtures only; CLINC150 data is **not** committed or fetched automatically to avoid ambiguous license/provenance and unnecessary CI download. Thus no actual external CLINC150 scores are reported yet.

## How to execute, after obtaining source data under authorized terms
```sh
cd research/agi_iteration001
sha256sum /path/to/data_small.json
python3 clinc_ood_protocol.py --clinc-json /path/to/data_small.json --sha256 <verified SHA256>
```
The SHA must come from the exact bytes retrieved from an independently verified original/official source. This is a cross-domain *exploratory* test, **not** evaluation of reasoning, AGI, original-label generalization, or scientific claims.

## Safeguards
No credentials, external API calls, agent activation, cloud instance creation, model promotion or production writes. Independent human review is still required for license, provenance, and label meaning. Stronger benchmark coverage is needed before proposing a model upgrade.
