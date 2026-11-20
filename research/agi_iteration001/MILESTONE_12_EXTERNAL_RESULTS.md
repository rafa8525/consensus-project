# Milestone 12 — actual external CLINC150 evaluation (full OOS split)

## Verified evidence
- **GitHub Actions full-run:** https://github.com/rafa8525/consensus-project/actions/runs/44684425824
- **Commit at evaluation:** `2cbd5e72c2b2e3bfe99ad8f41ee8128966032da7`
- **CI:** 115 tests passed; 55 proposed roles validated, none production-enabled.
- **Original CLINC150 source:** `https://github.com/clinc/oos-eval`; revision `828f8093932c8fe6ca7936c3d2e52903b1c523de`, `data/data_full.json`.
- **SHA-256 of exact source bytes verified in GitHub CI:** `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`.
- **Original upstream GitHub license:** CC BY 3.0 Unported (repository LICENSE). Note UCI's hosted distribution lists CC BY 4.0; cite the actual original file's terms and authors, not both interchangeably.
- **Original paper:** Larson et al., *An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction*, EMNLP 2019. https://aclanthology.org/D19-1131/

## Frozen cross-domain OOD evaluation
The selected candidate hyperparameters and the heuristic threshold were frozen from earlier research code; GitHub CI downloaded and checked source bytes before running. This is NOT a direct benchmark of our research-task labels; CLINC out-of-scope is defined relative to CLINC domains.

| Model | Original CLINC OOS queries accepted by vocabulary-coverage rule | Acceptance fraction |
|---|---:|---:|
| Word-only NB baseline | 299/1000 | 29.9% |
| Word + trigram NB candidate | 917/1000 | 91.7% |

At the same frozen threshold 0.25, the candidate's character n-grams frequently overlap ordinary English requests, causing high acceptance. **The feature-space coverage scales differ, so the rates cannot establish model-to-model calibrated superiority.** This exposes an important insufficiency in the OOD gate. No claim of improved OOD robustness is justified.

Internally authored 18-item confirmation set (not external):
- Baseline correctly classified and accepted 11/18; overall accepted 14/18.
- Candidate correctly classified and accepted 17/18; overall accepted 18/18.
- These measures must not be conflated with CLINC OOS accuracy.

**Decision:** no research or production promotion. `promotion_approved=false`. Do not tune thresholds on `oos_test`; it is now exposed and belongs to the final evaluation record. Next research cycle must use a separate OOD development set (e.g. CLINC `oos_val`, after reviewing relevance), freeze thresholds and compare on a truly untouched separate test split. For our own research-task classification, get independently labeled in-domain examples: CLINC classes are not direct stand-ins.

No production files changed, no agents deployed, no new paid compute or credentials. The original dataset was not committed into the AGI repository.
