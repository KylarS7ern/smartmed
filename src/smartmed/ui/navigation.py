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
    """Log-Screen vorbereiten und anzeigen."""
    log_screen = app.root.get_screen('log')
    log_screen.update_log()
    app.root.current = 'log'


def go_to_settings_menu(app):
    """Zum Einstellungsmenü wechseln."""
    app.root.current = 'settings_menu'