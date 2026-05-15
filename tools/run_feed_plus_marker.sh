#!/usr/bin/env bash
set -euo pipefail

# 1) Run the prediction feed
python3 /home/rafa1215/consensus-project/agents/prediction_feed_agent.py
echo "[gate] Running prediction feed training gate..."
python3 /home/rafa1215/consensus-project/tools/gates/prediction_feed_training_gate.py
echo "[gate] Prediction feed training gate passed."

# 2) Append Quick Actions block (canonical + mirror) if missing
python3 /home/rafa1215/consensus-project/tools/append_prediction_quick_actions.py

# 3) Write absorption public marker
python3 /home/rafa1215/consensus-project/tools/write_absorption_public_marker.py

# 4) Audit marker proving the task ran
mkdir -p /home/rafa1215/memory/logs/system/exec
echo "$(date -Iseconds) ok run_feed_plus_marker" >> /home/rafa1215/memory/logs/system/exec/run_feed_plus_marker.log
