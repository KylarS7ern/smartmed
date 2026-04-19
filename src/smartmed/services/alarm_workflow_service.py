from smartmed.services.schedule_service import (
    finde_ueberfaellige_offene_einnahmen,
    markiere_ueberfaellige_offene_einnahmen,
)


def collect_overdue_alarm_actions(offene_einnahmen: list) -> list[dict]:
    """Ermittelt überfällige offene Einnahmen und bereitet Alarm-Aktionen vor."""
    if not offene_einnahmen:
        return []

    ueberfaellige, _ = finde_ueberfaellige_offene_einnahmen(offene_einnahmen)

    if not ueberfaellige:
        return []

    return markiere_ueberfaellige_offene_einnahmen(ueberfaellige)

def process_overdue_alarm_actions(
    verarbeitete: list,
    trigger_alarm_callback,
) -> None:
    """Verarbeitet vorbereitete Alarm-Aktionen durch Aufruf des übergebenen Callbacks."""
    for eintrag in verarbeitete:
        trigger_alarm_callback(
            eintrag,
            console_text="ALARM: Einnahme NICHT bestätigt!",
            log_text="ALARM ausgelöst: Einnahme nicht bestätigt",
        )

def execute_alarm_action(
    *,
    eintrag: dict,
    console_text: str,
    log_text: str,
    log_callback,
    notify_callback,
    popup_callback,
    save_callback,
) -> None:
    """Führt eine Alarm-Aktion mit den übergebenen App-Callbacks aus."""
    print(console_text)
    log_callback(log_text)
    notify_callback(eintrag)
    popup_callback(eintrag)
    save_callback()