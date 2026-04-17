#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_ACTIVATE="$PROJECT_ROOT/.venv/bin/activate"

cd "$PROJECT_ROOT"

if [[ ! -f "$VENV_ACTIVATE" ]]; then
  echo "Fehler: Virtuelle Umgebung nicht gefunden unter: $VENV_ACTIVATE"
  exit 1
fi

source "$VENV_ACTIVATE"
export PYTHONPATH="$PROJECT_ROOT/src"

exec python -m smartmed.main