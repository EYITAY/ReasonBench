#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements-min.txt
echo "Minimal environment ready. Activate with: source .venv/bin/activate"