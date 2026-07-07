# SmartMediSpender

SmartMediSpender ist die Raspberry-Pi-Software für meinen Diplomarbeits-Prototypen zur automatischen Medikamentenausgabe.

Die Anwendung läuft auf einem Raspberry Pi mit Touchscreen und wurde mit Python und Kivy umgesetzt.

## Projektziel

Ziel ist eine saubere, wartbare und erweiterbare Finalsoftware für einen Medikamentenspender mit:

- Touch-Bedienung direkt am Gerät
- Benutzerverwaltung
- Einnahmeplan
- Ereignis- und Einnahmelogs
- Alarm- und Benachrichtigungslogik
- Anbindung an Arduino / Hardware für die tatsächliche Tablettenausgabe

## Architektur

- Die gesamte Projektstruktur liegt unter `src/smartmed/`, sauber nach Verantwortlichkeit aufgeteilt (`services/`, `ui/`, `hardware/`, `models/`)
- Die App wird über `python -m smartmed.main` gestartet
- Die App-Klasse `SmartMedGUI` (`src/smartmed/app.py`) ist ein dünner Orchestrator: sie hält den App-Zustand und verdrahtet Kivy-Callbacks (Timer, Touch-Events) mit der eigentlichen Geschäftslogik in `services/`
- Laufzeitdaten liegen in `data/smartmed_plan.json`

## Projektstruktur

    smartmed/
    ├─ data/
    ├─ scripts/
    ├─ src/
    │  └─ smartmed/
    │     ├─ app.py          # App-Klasse SmartMedGUI + create_app()
    │     ├─ main.py         # Einstiegspunkt (python -m smartmed.main)
    │     ├─ config.py
    │     ├─ models/
    │     ├─ services/       # gesamte Geschäftslogik
    │     ├─ hardware/       # Arduino-Transport (real + Mock)
    │     └─ ui/             # Screens, Popups, Theme, Widgets
    ├─ tests/
    ├─ pyproject.toml
    ├─ README.md

## Voraussetzungen

- Raspberry Pi
- Python 3.13
- virtuelle Umgebung `.venv`
- Kivy 2.3.1
- requests 2.33.0

## Projekt lokal auf dem Raspberry Pi starten

### 1. Ins Projekt wechseln

    cd ~/projects/smartmed

### 2. Virtuelle Umgebung aktivieren

    source .venv/bin/activate

### 3. App starten

Empfohlener Startweg:

    ./scripts/run_pi.sh

Alternativ direkt:

    export PYTHONPATH=src
    python -m smartmed.main

## Lokale Entwicklung unter Windows / VS Code

Die App lässt sich auch ohne angeschlossenen Raspberry Pi / Arduino auf einem
normalen Windows-Laptop starten und testen (z.B. um Änderungen vorab zu prüfen,
bevor sie aufs Pi kommen).

### 1. Virtuelle Umgebung erstellen

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -e .

### 2. `.env` für lokale Entwicklung anlegen

    copy .env.example .env

In der `.env` folgende zwei Werte setzen (Rest kann leer bleiben):

    SMARTMED_HARDWARE_MODE=mock
    SMARTMED_KIOSK=0

- `SMARTMED_HARDWARE_MODE=mock` simuliert den Arduino (kein echtes Gerät nötig, PING/DISPENSE liefern plausible Antworten).
- `SMARTMED_KIOSK=0` öffnet ein normales, verschiebbares/schliessbares Fenster statt des Vollbild-Kiosk-Modus vom echten Gerät.

Auf dem Pi bleibt `.env` wie bisher (bzw. beide Werte einfach weglassen = Standardverhalten unverändert: echte Hardware, Vollbild-Kiosk).

### 3. App starten

    $env:PYTHONPATH = "src"
    python -m smartmed.main

Oder direkt in VS Code über **Run and Debug** → "SmartMed: App starten (lokal)" (siehe `.vscode/launch.json`).

### 4. Tests ausführen

    python -m unittest discover -s tests

Oder in VS Code über den Test-Explorer (Test-Framework ist in `.vscode/settings.json` bereits auf `unittest` konfiguriert) bzw. die Debug-Konfiguration "SmartMed: Alle Tests ausführen".

## Datenablage

Die aktive Datendatei ist:

    data/smartmed_plan.json

Diese Datei wird von der App beim Start geladen und beim Speichern aktualisiert.

## Entwicklungsansatz

Entwickelt wird aktuell direkt auf dem Raspberry Pi mit Visual Studio Code per Remote-SSH.

Warum dieser Weg:

- direktes Testen auf dem echten Touchscreen
- echtes Verhalten von Kivy auf dem Zielgerät
- spätere Hardware-Anbindung besser testbar
- weniger Komplexität als Docker / Dev Container für diese Projektphase

## Autostart auf dem Pi einrichten

Damit die App direkt beim Einschalten des Pi erscheint (Raspberry Pi OS Desktop
mit Autologin), gibt es einen XDG-Autostart-Eintrag.

### Einmalig einrichten

    cd ~/projects/smartmed
    ./scripts/install_autostart.sh

Das kopiert `scripts/smartmed-autostart.desktop` nach `~/.config/autostart/`
und macht die Start-Skripte ausführbar. Beim nächsten Neustart/Login startet
die App automatisch über `scripts/run_pi_resilient.sh` (wartet kurz auf die
USB/Serial-Enumeration und startet die App bei einem unerwarteten Absturz neu;
Log dazu in `logs/autostart.log`).

### Wieder deaktivieren

    rm ~/.config/autostart/smartmed-autostart.desktop

## Nächste technische Ziele

- Tabletten-Erkennung per Sensor (Lichtschranke) inkl. Retry-Logik, sobald die Sensor-Hardware verbaut ist
- Missed-Dose-Erkennung nach einem App-Neustart

## Hinweise

- `data/smartmed_plan.json` ist die aktuelle Quelle der Wahrheit für Laufzeitdaten
