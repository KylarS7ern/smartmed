import json
import os
import tempfile
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
    """Speichert JSON-Daten atomar in eine Datei.

    Schreibt zuerst vollständig in eine temporäre Datei im selben
    Verzeichnis und ersetzt die Zieldatei erst danach in einem einzigen
    Dateisystem-Schritt (os.replace). Bei einem Stromausfall/Absturz mitten
    im Speichern bleibt so immer die alte, vollständige Datei erhalten
    statt einer halb geschriebenen/leeren.

    Gibt True bei Erfolg, sonst False zurück.
    """
    try:
        data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=data_file.parent, prefix=f".{data_file.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, data_file)
        except BaseException:
            os.unlink(tmp_path)
            raise

        print(f"Daten in '{data_file}' gespeichert.")
        return True
    except Exception as e:
        print("Fehler beim Speichern der Daten:", e)
        return False
