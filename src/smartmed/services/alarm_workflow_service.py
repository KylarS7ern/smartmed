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