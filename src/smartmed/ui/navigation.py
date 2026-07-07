def go_to_login(app):
    """Zur Benutzer-Auswahl zurückkehren."""
    app.root.current = 'login'


def go_to_menu(app):
    """Ins Hauptmenü wechseln."""
    app.root.current = 'menu'


def go_to_status(app):
    """Status-Screen vorbereiten und anzeigen."""
    status_screen = app.root.get_screen('status')
    status_screen.tages_offset = 0
    status_screen.update_status()
    app.root.current = 'status'


def go_to_plan_list(app):
    """Planliste vorbereiten und anzeigen."""
    plan_screen = app.root.get_screen('plan_list')
    plan_screen.update_liste()
    app.root.current = 'plan_list'


def go_to_log(app):
    """Log-Screen anzeigen (aktualisiert sich selbst über on_pre_enter)."""
    app.root.current = 'log'


def go_to_settings_menu(app):
    """Zum Einstellungsmenü wechseln."""
    app.root.current = 'settings_menu'

def go_to_settings_patient(app):
    """Zu den Patienten-Einstellungen wechseln."""
    app.root.current = 'settings_patient'


def go_to_settings(app):
    """Zu den Alarm-Einstellungen wechseln."""
    app.root.current = 'settings'


def go_to_settings_advanced(app):
    """Zu den erweiterten Einstellungen wechseln."""
    app.root.current = 'settings_advanced'


def go_to_plan_edit(app, eintrag=None):
    """Plan-Edit-Screen vorbereiten und öffnen."""
    edit_screen = app.root.get_screen('plan_edit')

    if eintrag is None:
        edit_screen.felder_zuruecksetzen()
    else:
        edit_screen.start_bearbeiten(eintrag)

    app.root.current = 'plan_edit'