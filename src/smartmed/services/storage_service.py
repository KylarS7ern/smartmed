import json
from pathlib import Path


def load_json_data(data_file: Path) -> dict:
    """Lädt JSON-Daten aus einer Datei.

    Gibt bei fehlender Datei ein leeres Dictionary zurück.
    """
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Noch keine gespeicherten Daten vorhanden, starte leer.")
        return {}
    except Exception as e:
        print("Fehler beim Laden der Daten:", e)
        return {}


def save_json_data(data_file: Path, data: dict) -> bool:
    """Speichert JSON-Daten in eine Datei.

    Gibt True bei Erfolg, sonst False zurück.
    """
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Daten in '{data_file}' gespeichert.")
        return True
    except Exception as e:
        print("Fehler beim Speichern der Daten:", e)
        return False
