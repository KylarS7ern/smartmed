from datetime import datetime
from pathlib import Path

from smartmed.services.storage_service import load_json_data, save_json_data

BACKUP_DATEI_PRAEFIX = "smartmed_backup_"


def export_data_to_file(data: dict, export_dir: Path, *, now=None) -> Path:
    """Exportiert die komplette App-Datenbank (alle Benutzer, Admin-PIN,
    Fachbelegung) als Sicherungsdatei, damit sie z.B. vor einem
    SD-Kartentausch extern aufbewahrt werden kann (USB-Stick, E-Mail)."""
    export_dir.mkdir(parents=True, exist_ok=True)
    now = now or datetime.now()
    dateiname = f"{BACKUP_DATEI_PRAEFIX}{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    pfad = export_dir / dateiname
    save_json_data(pfad, data)
    return pfad


def list_backup_files(export_dir: Path) -> list:
    """Listet vorhandene Sicherungsdateien im Exportordner, neueste zuerst."""
    if not export_dir.exists():
        return []
    return sorted(export_dir.glob(f"{BACKUP_DATEI_PRAEFIX}*.json"), reverse=True)


def load_backup_file(pfad: Path) -> dict:
    """Lädt und validiert minimal eine Sicherungsdatei vor der Wiederherstellung."""
    data = load_json_data(pfad)
    if not isinstance(data, dict) or "users" not in data:
        raise ValueError("Datei ist keine gültige SmartMediSpender-Sicherung.")
    return data
