# Milestone 8 — independently measured experiment result

GitHub Actions run: https://github.com/rafa8525/consensus-project/actions/runs/44678963898

Verified commit: `4f8250945050b322b0ef282cd2678c6e865ce9d6`

CI: **85 tests passed, zero failed**. Research registry: 55 unique proposed role definitions, none production enabled.

Experiment: `char_ngram_nb_vs_word_nb_v1`
Dataset checksum: `bc1bee520c7398f312e2d2ac58bc3e016b4885a38d9ecb579f9415c0a16faf8c`
Train 18, validation 12, test 12; all hand-authored class-balanced examples.

| Model | Validation correct | Validation accuracy | Test correct | Test accuracy |
|---|---:|---:|---:|---:|
| Word-only multinomial NB baseline | 6/12 | 50% | 9/12 | 75% |
| Unigram + character-trigram NB candidate | 9/12 | 75% | 9/12 | 75% |

Selected candidate: n=3, alpha=0.5. Candidate was chosen on validation after testing nine combinations; held-out test did **not** improve.

Result of the experiment's predeclared gate: `promotion_approved: true` for **research checkpoint only** because validation improved and the test did not regress. **No production promotion**, deployment, weights replacement, autonomous agents, or live system changes occurred.

Interpretation: The candidate has a promising validation signal, **not confirmed superiority on independent held-out test data**. The evaluation has very low statistical power and is vulnerable to handcrafted lexical patterns. Do not claim actual AGI capability.

Next iteration: gather or hand-label more genuinely disjoint examples before any further model selection; evaluate across multiple fixed splits with seed logging, macro-F1 and uncertainty; enforce a stronger promotion condition requiring improvement on an untouched external test set. Resource consumption should be recorded by CI, and model training must remain within existing compute.
