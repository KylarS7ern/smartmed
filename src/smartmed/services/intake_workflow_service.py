from smartmed.services.dispense_service import dispense_due_entries
from smartmed.services.schedule_service import (
    berechne_alarm_delay_minuten,
    erstelle_offene_einnahmen,
    finde_faellige_einnahmen,
)


def prepare_due_intake_workflow(
    *,
    plan_eintraege: list,
    offene_einnahmen: list,
    settings: dict,
    last_popup_minute,
    jetzt=None,
) -> dict | None:
    """Ermittelt aktuell fällige Einnahmen, ohne bereits zu dispensieren."""
    if not plan_eintraege:
        return None

    due, jetzt, minute_key, tag_kurz, zeit_str = finde_faellige_einnahmen(
        plan_eintraege, jetzt=jetzt
    )

    if last_popup_minute == minute_key:
        return None

    if not due:
        return None

    delay_min = berechne_alarm_delay_minuten(
        settings.get("alarm_delay_min", 30)
    )

    return {
        "due": due,
        "jetzt": jetzt,
        "minute_key": minute_key,
        "tag_kurz": tag_kurz,
        "zeit_str": zeit_str,
        "delay_min": delay_min,
    }


def execute_due_intake_workflow(*, transport, prepared: dict, offene_einnahmen: list) -> dict:
    """Dispensiert die fälligen Einträge und bereitet die Bestätigungs-Trackinginfo vor.

    Nur erfolgreich dispensierte Einträge werden zur Einnahme-Bestätigung
    vorgemerkt (offene_einnahmen) – für nicht ausgegebene Tabletten darf nie
    eine Einnahme-Bestätigung verlangt werden.
    """
    dispense_result = dispense_due_entries(transport, prepared["due"])
    dispensed_eintraege = [item["eintrag"] for item in dispense_result["dispensed"]]

    neue_offene = (
        erstelle_offene_einnahmen(
            due=dispensed_eintraege,
            offene_einnahmen=offene_einnahmen,
            jetzt=prepared["jetzt"],
            delay_min=prepared["delay_min"],
            tag_kurz=prepared["tag_kurz"],
            zeit_str=prepared["zeit_str"],
        )
        if dispensed_eintraege
        else []
    )

    return {
        "dispensed_eintraege": dispensed_eintraege,
        "neue_offene": neue_offene,
        "failed": dispense_result["failed"],
        "jetzt": prepared["jetzt"],
    }
