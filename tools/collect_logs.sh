#!/bin/bash

# Robust log collection script for PythonAnywhere
# Handles missing directories and provides clear feedback

echo "=== Consensus Project Log Collector ==="

# Get absolute path to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Working directory: $PROJECT_ROOT"

# Generate timestamp filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUT="agent_logs_${TIMESTAMP}.tar.gz"

echo "Creating archive: $OUT"

# Define log paths to collect
LOG_PATHS=(
    "memory/logs/heartbeat"
    "memory/logs/github_sync"
    "memory/logs/system"
    "memory/logs/agents"
    "memory/logs/fitness"
    "memory/logs/finance"
    "memory/logs/voice"
    "memory/logs/transit"
    "nohup.out"
)

# Check which paths exist
EXISTING_PATHS=()
MISSING_PATHS=()

for path in "${LOG_PATHS[@]}"; do
    if [[ -e "$path" ]]; then
        EXISTING_PATHS+=("$path")
        echo "✓ Found: $path"
    else
        MISSING_PATHS+=("$path")
        echo "✗ Missing: $path"
    fi
done

# Show summary
echo ""
echo "Found ${#EXISTING_PATHS[@]} paths, missing ${#MISSING_PATHS[@]} paths"

if [[ ${#EXISTING_PATHS[@]} -eq 0 ]]; then
    echo "ERROR: No log files or directories found!"
    echo "Current directory contents:"
    ls -la
    exit 1
fi

# Create archive with only existing paths
echo ""
echo "Creating tar archive..."
if tar -czf "$OUT" "${EXISTING_PATHS[@]}" 2>&1; then
    if [[ -f "$OUT" ]]; then
        FILESIZE=$(stat -c%s "$OUT" 2>/dev/null || echo "unknown")
        echo ""
        echo "SUCCESS! Created: $OUT"
        echo "File size: $FILESIZE bytes"
        echo "Location: $PROJECT_ROOT/$OUT"
        echo ""
        echo "Archive contents:"
        tar -tzf "$OUT" | head -10
        if [[ $(tar -tzf "$OUT" | wc -l) -gt 10 ]]; then
            echo "... and $(($(tar -tzf "$OUT" | wc -l) - 10)) more files"
        fi
        echo ""
        echo "✅ Upload this file: $OUT"
    else
        echo "ERROR: Archive creation appeared to succeed but file not found!"
        exit 1
    fi
else
    echo "ERROR: Failed to create archive"
    exit 1
fi
