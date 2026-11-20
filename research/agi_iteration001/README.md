# Project AGI — Iteration 001
Isolated experimental work. **Do not merge into production without review.**

This is a standard-library-only neural-network training smoke test, not AGI and not proof of generalization. The 17-parameter 2–4–1 MLP is trained on all four XOR examples and compared with a 3-parameter linear logistic baseline. The evaluation uses the training data; no held-out set is available for a four-case truth table.

Run from this directory:
```sh
python3 train.py --out results.json
python3 -m unittest -v test_train.py
```

Local verified result (2026-11-19): 4/4 MLP, 2/4 linear baseline, 3 tests passed. Reproduce in an independent environment before calling it independently verified.

Production safeguard: no changes to ACS-01 through ACS-05, schedules, CI, secrets, cloud resources or production runtime. This branch is not merged.

Next milestone: verify 55-agent inventory, resolve ACS-03/05 concerns, inventory compute and independently reproduce training; then design a meaningful held-out generalization benchmark.
