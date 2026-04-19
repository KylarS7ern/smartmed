def build_runtime_state_defaults() -> dict:
    """Erzeugt die Standardwerte für nicht-persistenten Laufzeitzustand."""
    return {
        "offene_einnahmen": [],
        "_last_popup_minute": None,
    }


def reset_runtime_state(app) -> None:
    """Setzt nicht-persistenten Laufzeitzustand auf definierte Standardwerte zurück."""
    for key, value in build_runtime_state_defaults().items():
        setattr(app, key, value)