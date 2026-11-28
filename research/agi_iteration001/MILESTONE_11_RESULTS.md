# Milestone 11 — Verified independent-source OOD protocol (not externally executed)

**CI:** https://github.com/rafa8525/consensus-project/actions/runs/44684081819  
**Verified code commit:** `70ea9daef339412c051983421d4e0b3aa75d712f`
**Result:** 115 tests passed; registry confirms 55 distinct *proposed* roles, zero production-enabled.

## Source review
- CLINC150, original authors: https://github.com/clinc/oos-eval
- UCI CLINC150: https://archive.ics.uci.edu/dataset/570/clinc150
- Paper: https://aclanthology.org/D19-1131/

The official repository describes crowdsourced intent phrases, 150 supported intent classes and 1,000 `oos_test` examples in the full set. UCI reports CC BY 4.0 for its hosted dataset; the original GitHub source may have different licensing, so review the **exact downloaded distribution's license** before reuse or redistribution.

## What CI actually verified
- Original-format `oos_test` reader with checksum, sample cap, symlink refusal, distinct queries and label enforcement
- Stable sample selection independent of model outputs
- Evaluation of fixed baseline and candidate on an out-of-domain *lexical-coverage* acceptance rule
- Clear separation from research-task classification and an unconditional `promotion_approved=false`
- Nine focused synthetic-fixture tests; no CLINC150 data or external dataset used in CI

**No external CLINC150 benchmark score was obtained or claimed.** Raw source retrieval is not part of the current CI, and the test labels are incompatible with the existing three research-task categories. The source-evaluation gate is ready to run offline against an authorized, checksum-pinned local copy.

## Next useful milestone
Acquire verified external benchmark data and record its actual SHA-256, independent license and version. Execute frozen OOD comparison in an isolated environment and publish measured false-accept rates. Separately source independently labeled *research-task* samples before any candidate promotion. Expand evaluation beyond simple task classification to reasoning, planning and error diagnosis while retaining stringent compute, security and approval boundaries.

No production writes, deployments, cloud purchases, ACS changes, or 55-agent fleet activation.
