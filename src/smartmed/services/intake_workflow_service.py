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
) -> dict | None:
    """Bereitet die Verarbeitung aktuell fälliger Einnahmen vor."""
    if not plan_eintraege:
        return None

    due, jetzt, minute_key, tag_kurz, zeit_str = finde_faellige_einnahmen(
        plan_eintraege
    )

    if last_popup_minute == minute_key:
        return None

    if not due:
        return None

    delay_min = berechne_alarm_delay_minuten(
        settings.get("alarm_delay_min", 30)
    )

    neue_offene = erstelle_offene_einnahmen(
        due=due,
        offene_einnahmen=offene_einnahmen,
        jetzt=jetzt,
        delay_min=delay_min,
        tag_kurz=tag_kurz,
        zeit_str=zeit_str,
    )

    return {
        "due": due,
        "jetzt": jetzt,
        "minute_key": minute_key,
        "neue_offene": neue_offene,
    }