def build_runtime_state_defaults() -> dict:
    """Erzeugt die Standardwerte für nicht-persistenten Laufzeitzustand.

    offene_einnahmen gehört bewusst NICHT hierher: die wird pro Benutzer
    persistiert (siehe user_state_service.py), damit unbestätigte
    Einnahmen einen Neustart/Benutzerwechsel überstehen statt
    stillschweigend zu verschwinden.
    """
    return {
        "_last_popup_minute": None,
    }


def reset_runtime_state(app) -> None:
    """Setzt nicht-persistenten Laufzeitzustand auf definierte Standardwerte zurück."""
    for key, value in build_runtime_state_defaults().items():
        setattr(app, key, value)