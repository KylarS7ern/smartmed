#!/usr/bin/env bash
# Einmalig auf dem Raspberry Pi ausführen, um den Autostart einzurichten:
#   ./scripts/install_autostart.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"

mkdir -p "$AUTOSTART_DIR"
chmod +x "$SCRIPT_DIR/run_pi.sh" "$SCRIPT_DIR/run_pi_resilient.sh"

# Wird hier statt aus einer statischen Vorlage erzeugt, damit der Pfad zum
# tatsächlichen Projektordner passt, egal wo dieser liegt (nicht jeder
# checkt das Repo nach ~/projects/smartmed aus).
cat > "$AUTOSTART_DIR/smartmed-autostart.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=SmartMediSpender
Comment=Startet die SmartMediSpender-App automatisch nach dem Login
Exec=/bin/bash -lc "$PROJECT_ROOT/scripts/run_pi_resilient.sh"
X-GNOME-Autostart-enabled=true
NoDisplay=false
Terminal=false
EOF

echo "Autostart eingerichtet: $AUTOSTART_DIR/smartmed-autostart.desktop"
echo "Beim nächsten Login/Neustart startet die App automatisch."
echo "Deaktivieren: rm '$AUTOSTART_DIR/smartmed-autostart.desktop'"
