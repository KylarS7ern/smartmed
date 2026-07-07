#!/usr/bin/env bash
# Wrapper um run_pi.sh für den Autostart: wartet kurz auf die USB/Serial-
# Enumeration (Arduino) nach dem Boot und startet die App bei einem
# unerwarteten Absturz automatisch neu, statt dass der Bildschirm leer bleibt.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/autostart.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Autostart-Wrapper gestartet." >> "$LOG_FILE"

# USB/Serial-Geräte (Arduino) brauchen nach dem Boot etwas Zeit, bis sie
# enumeriert sind.
sleep 5

while true; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starte SmartMedSpender..." >> "$LOG_FILE"

  "$SCRIPT_DIR/run_pi.sh" >> "$LOG_FILE" 2>&1
  exit_code=$?

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] App beendet mit Exit-Code $exit_code." >> "$LOG_FILE"

  if [[ $exit_code -eq 0 ]]; then
    # Normal beendet (z.B. "App beenden" im Login-Screen) -> nicht neu starten.
    break
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Unerwarteter Absturz, Neustart in 3s..." >> "$LOG_FILE"
  sleep 3
done
