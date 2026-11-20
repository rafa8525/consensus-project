# Milestone 10 — verified stress and resource benchmark

**GitHub Actions:** https://github.com/rafa8525/consensus-project/actions/runs/44680062716  
**Verified commit:** `113e1a6054a1062283ba5337e8757b405d035b77`  
**CI result:** 106/106 automated tests pass; research registry validator passed for 55 unique **proposed, not production-enabled** role entries.

## Hand-authored stress probe: 12 texts
| Metric | Word NB baseline | Character-trigram + word NB candidate |
|---|---:|---:|
| Correct | 11/12 | 12/12 |
| Accuracy | 91.6667% | 100% |
| Macro-F1 | 0.915344 | 1.0 |
| Training time (ms) | 0.630 | 3.810 |
| Training peak traced allocation (KiB) | 28.84 | 117.42 |
| Inference time, 12 texts (ms) | 0.918 | 2.439 |
| Inference peak traced allocation (KiB) | 10.85 | 6.70 |

Measurements are single-run Python `tracemalloc` and monotonic wall clock, **not process RSS** or guaranteed resource limits. Precision exceeds stability; repeat measurements are needed.

**Important:** The internal stress texts were drafted by the same research process and may resemble training examples. This is not independent externally sourced testing. It does not demonstrate AGI, recursive model self-improvement, or production capability. No model promotion was performed.

## External dataset validation boundary
The `external_benchmark_gate.py` program accepts up to 5000 labeled examples with a SHA-256 manifest, declared HTTPS source, license, annotation and collection details, disjoint normalized exact texts, balanced labels, and bounded file sizes. Its 12 unit tests use **synthetic fixtures** only. An accepted manifest does not cryptographically prove collection provenance or independent annotation. Accordingly the evaluator returns `independent_provenance_verified=false` and `promotion_approved=false` without any option to override these through the manifest.

## Next experiment
Acquire a genuinely independently curated, licensed task-intent evaluation corpus with all three labels; obtain separate human review of label and provenance, freeze manifest and checksum prior to model evaluation; apply an updated promotion gate requiring significant independent accuracy and macro-F1 gain. Keep the 55 agent fleet conceptual until live instances are separately verified. No merges, production writes, cloud spending or automatic deployment.
