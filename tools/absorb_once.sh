#!/bin/bash
set +e
cd "$HOME/consensus-project" 2>/dev/null || true
mkdir -p memory/logs/scheduler
echo "$(date -Is) absorb_once.sh placeholder executed" >> memory/logs/scheduler/placeholder_absorb.log
exit 0
