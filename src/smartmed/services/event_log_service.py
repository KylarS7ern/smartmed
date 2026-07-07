from datetime import datetime, timedelta
from pathlib import Path

TIMESTAMP_FORMAT = "%d.%m.%Y %H:%M:%S"


def append_log_entry(log_entries: list, text: str, now: datetime | None = None) -> dict:
    """Hängt einen Log-Eintrag mit Zeitstempel an die übergebene Log-Liste an."""
    timestamp = (now or datetime.now()).strftime(TIMESTAMP_FORMAT)
    entry = {
        "timestamp": timestamp,
        "text": text,
    }
    log_entries.append(entry)
    return entry


def get_log_entry_timestamp(entry: dict) -> str:
    """Liest den Zeitstempel eines Log-Eintrags robust aus.

    Unterstützt:
    - neues Format: 'timestamp'
    - altes Format: 'zeit'
    """
    return entry.get("timestamp") or entry.get("zeit") or ""


def prune_old_entries(log_entries: list, days: int = 30, now: datetime | None = None) -> list:
    """Entfernt Log-Einträge, die älter als 'days' Tage sind.

    Einträge mit nicht auswertbarem Zeitstempel werden sicherheitshalber behalten,
    damit nie versehentlich Daten verloren gehen (Lastenheft: Protokoll wird
    mindestens 30 Tage aufbewahrt).
    """
    cutoff = (now or datetime.now()) - timedelta(days=days)

    behalten = []
    for entry in log_entries:
        ts_text = get_log_entry_timestamp(entry)
        try:
            ts = datetime.strptime(ts_text, TIMESTAMP_FORMAT)
        except (ValueError, TypeError):
            behalten.append(entry)
            continue

        if ts >= cutoff:
            behalten.append(entry)

    return behalten


def format_log_as_text(log_entries: list, *, patient_name: str = "", exportiert_am: datetime | None = None) -> str:
    """Formatiert das Ereignisprotokoll als lesbaren Klartext (für Export/E-Mail)."""
    zeitstempel = (exportiert_am or datetime.now()).strftime(TIMESTAMP_FORMAT)

    zeilen = [
        "SmartMediSpender - Ereignisprotokoll",
        f"Patient: {patient_name or '-'}",
        f"Exportiert am: {zeitstempel}",
        "-" * 40,
        "",
    ]

    if not log_entries:
        zeilen.append("Keine Log-Einträge vorhanden.")
    else:
        for entry in log_entries:
            ts = get_log_entry_timestamp(entry)
            text = entry.get("text", "")
            zeilen.append(f"{ts} - {text}")

    return "\n".join(zeilen) + "\n"


def export_log_to_file(
    log_entries: list,
    export_dir: Path,
    *,
    patient_name: str = "",
    now: datetime | None = None,
) -> Path:
    """Schreibt das Ereignisprotokoll als .txt-Datei und gibt den Pfad zurück."""
    now = now or datetime.now()
    export_dir.mkdir(parents=True, exist_ok=True)

    dateiname = f"log_export_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    pfad = export_dir / dateiname

    inhalt = format_log_as_text(log_entries, patient_name=patient_name, exportiert_am=now)
    pfad.write_text(inhalt, encoding="utf-8")

    return pfad