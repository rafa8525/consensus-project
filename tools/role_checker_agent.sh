#!/bin/bash
# tools/role_checker_agent.sh
# Console-safe nightly audit of agent duties
# This script will NEVER close your PythonAnywhere console

CSV_FILE="memory/agents/roles.csv"
REPORT="memory/logs/system/role_checker_report.md"

TS=$(date +%Y-%m-%dT%H:%M:%S)
mkdir -p "$(dirname "$REPORT")" || true

echo "[$TS] 🔍 Running role-checker agent..." | tee -a "$REPORT"

if [[ ! -f "$CSV_FILE" ]]; then
  echo "[$TS] ❌ roles.csv missing — cannot audit agent coverage." | tee -a "$REPORT"
else
  while IFS=, read -r agent role path; do
    [[ -z "$agent" || "$agent" == "Agent" ]] && continue
    if [[ -n "$path" && ! -e $path ]]; then
      echo "[$TS] ⚠️ $agent ($role) is missing expected log/file at $path" | tee -a "$REPORT"
      echo "   👉 Recommendation: Verify $role is implemented. If missing, create/update $path." | tee -a "$REPORT"
    else
      echo "[$TS] ✅ $agent ($role) OK — log/file found." | tee -a "$REPORT"
    fi
  done < "$CSV_FILE"
fi

echo "[$TS] 🎯 Role-check complete. Console remains open." | tee -a "$REPORT"
