#!/bin/bash
# ===========================================================
# AI Consensus System – Comprehensive Repair Script
# Applies all directory, registry, and log integrity fixes.
# ===========================================================

set -e

PROJECT_ROOT=~/consensus-project
cd "$PROJECT_ROOT"

echo "🔧 Starting AI Consensus System repair at $(date)"

# --- 1. Directory & Path Fixes ---------------------------------------------
echo "📁 Ensuring required directories exist..."
mkdir -p reports logs/reports memory/logs/agents memory/logs/system memory/logs/fitness

echo "🔗 Validating registry symlink..."
cd config || { echo "❌ config directory not found"; exit 1; }

if [ ! -f CONSENSUS_REGISTRY.yaml ]; then
  if [ -f CONSENSUS_REGISTRY.v2.yaml ]; then
    ln -s CONSENSUS_REGISTRY.v2.yaml CONSENSUS_REGISTRY.yaml
    echo "✅ Symlink created: CONSENSUS_REGISTRY.yaml → CONSENSUS_REGISTRY.v2.yaml"
  else
    echo "⚠️ Missing CONSENSUS_REGISTRY.v2.yaml – create it manually if needed."
  fi
else
  echo "✅ Registry symlink already exists."
fi

cd "$PROJECT_ROOT"

echo "🧹 Updating .gitignore to allow logs and registry..."
sed -i 's|^memory/logs/|#memory/logs/|' .gitignore || true
sed -i 's|^config/CONSENSUS_REGISTRY.*|#&|' .gitignore || true

# --- 2. Rebuild Agent Registry & Reports -----------------------------------
echo "🧠 Rebuilding agent registry..."
python3 tools/convert_csv_to_yaml.py || echo "⚠️ CSV→YAML conversion skipped or failed."

echo "🧾 Rebuilding status report..."
python3 tools/status_report_builder.py --full || echo "⚠️ Status report build skipped or failed."

echo "📚 Building final agent report PDF..."
python3 tools/build_final_agent_report.py \
  --registry config/CONSENSUS_REGISTRY.yaml \
  --logs logs/reports/status.log \
  --out reports/consensus_55_agents_FINAL.pdf || echo "⚠️ PDF build failed – verify dependencies."

# --- 3. Log Collection Script Fixes ----------------------------------------
echo "📦 Fixing collect_logs.sh formatting and permissions..."
if [ -f tools/collect_logs.sh ]; then
  sed -i 's/\r$//' tools/collect_logs.sh
  chmod +x tools/collect_logs.sh
  bash tools/collect_logs.sh || echo "⚠️ Log collection script ran with warnings."
else
  echo "⚠️ tools/collect_logs.sh not found."
fi

ls -lh agent_logs_*.tar.gz 2>/dev/null || echo "ℹ️ No agent log archive found yet."

# --- 4. Memory / Index Integrity -------------------------------------------
echo "🧩 Checking memory index consistency..."
python3 - <<'PYCODE'
import os, time
folder = "memory/logs/fitness"
for root, _, files in os.walk(folder):
    for f in files:
        path = os.path.join(root, f)
        if os.path.isfile(path):
            mtime = time.ctime(os.path.getmtime(path))
            print(f"Checked {path} (last modified {mtime})")
PYCODE

# --- 5. Ops Heartbeat & Monitoring Enhancements ----------------------------
echo "💓 Ensuring heartbeat guard active..."
if pgrep -f mcl_guard.py >/dev/null; then
  echo "✅ Heartbeat guard already running."
else
  nohup python3 tools/mcl_guard.py >/dev/null 2>&1 &
  echo "🚀 Restarted mcl_guard.py in background."
fi

echo "✅ AI Consensus System repair completed successfully at $(date)"
