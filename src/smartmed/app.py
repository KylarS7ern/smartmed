from legacy.gui import SmartMedGUI


def create_app() -> SmartMedGUI:
    """Erstellt die App-Instanz.

    Vorerst wird noch der bestehende Legacy-Prototyp verwendet.
    Später wird diese Datei der zentrale Einstieg in die neue Architektur.
    """
    return SmartMedGUI()