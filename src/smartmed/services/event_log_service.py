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