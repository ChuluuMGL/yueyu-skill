#!/usr/bin/env bash
# Run the full local yueyu-skill QA gate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

section() {
  printf '\n== %s ==\n' "$1"
}

section "Manifest"
bash scripts/check_manifest.sh

section "Assets"
python3 scripts/check_assets.py

section "Live Drift"
STRICT_SERVER_ANYOF="${STRICT_SERVER_ANYOF:-1}" python3 scripts/check_mcp_drift.py

section "MCP Smoke"
if [ "$#" -gt 0 ]; then
  bash scripts/mcp_smoke_test.sh "$1"
else
  bash scripts/mcp_smoke_test.sh
fi
