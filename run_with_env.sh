#!/bin/bash
set -euo pipefail

# Always load the canonical env file using an absolute path (safe for scheduled tasks)
set -a
source "/home/rafa1215/reminder-api/.env"
set +a

# Always run from the project directory (also absolute for scheduled tasks)
cd "/home/rafa1215/consensus-project"

# Run python with whatever args you pass (script path, -c, -m, etc.)
exec /usr/bin/python3 "$@"
