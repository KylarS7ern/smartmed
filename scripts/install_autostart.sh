#!/usr/bin/env bash
# Einmalig auf dem Raspberry Pi ausführen, um den Autostart einzurichten:
#   ./scripts/install_autostart.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"

mkdir -p "$AUTOSTART_DIR"
chmod +x "$SCRIPT_DIR/run_pi.sh" "$SCRIPT_DIR/run_pi_resilient.sh"

cp "$SCRIPT_DIR/smartmed-autostart.desktop" "$AUTOSTART_DIR/smartmed-autostart.desktop"

echo "Autostart eingerichtet: $AUTOSTART_DIR/smartmed-autostart.desktop"
echo "Beim nächsten Login/Neustart startet die App automatisch."
echo "Deaktivieren: rm '$AUTOSTART_DIR/smartmed-autostart.desktop'"
