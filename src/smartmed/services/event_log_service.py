from datetime import datetime


def append_log_entry(log_entries: list, text: str, now: datetime | None = None) -> dict:
    """Hängt einen Log-Eintrag mit Zeitstempel an die übergebene Log-Liste an."""
    timestamp = (now or datetime.now()).strftime("%d.%m.%Y %H:%M:%S")
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