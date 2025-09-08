#!/usr/bin/env bash
set -e
echo "== validate_mcl_v2 =="
PROJECT_DIR="${PROJECT_DIR:-$HOME/consensus-project}"
cd "$PROJECT_DIR"

python3.10 -m py_compile mcl_v2/*.py smoke_test.py
python3.10 smoke_test.py
echo "== ledger tail =="
tail -n 10 memory/logs/system/sms_ledger.jsonl || true
echo "== validate_mcl_v2: OK =="
