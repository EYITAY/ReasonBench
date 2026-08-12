#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Prefer venv python explicitly
if [ ! -x ".venv/bin/python" ]; then
  echo ".venv not found; run scripts/setup_min.sh first." >&2
  exit 1
fi

.venv/bin/python src/run_collection.py --models gpt-4o claude-sonnet-4-5 --dry-run