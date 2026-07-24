from smartmed.models.defaults import build_default_user
from smartmed.services.security_service import hash_secret, is_hashed, verify_secret


def list_sorted_usernames(users):
    """Gibt die Benutzernamen sortiert zurück."""
    return sorted(users.keys())


def user_requires_password(users, username):
    """Prüft, ob für den Benutzer ein Passwort gesetzt ist."""
    user = users.get(username, {})
    gespeichertes_pw = user.get('password', '')
    return bool(gespeichertes_pw)


def verify_user_password(users, username, password_input):
    """Prüft ein eingegebenes Passwort gegen den gespeicherten (gehashten oder alten Klartext-) Benutzer."""
    user = users.get(username, {})
    gespeichertes_pw = user.get('password', '')

    if not gespeichertes_pw:
        return {
            'ok': True,
            'message': '',
            'needs_rehash': False,
        }

    if verify_secret(gespeichertes_pw, password_input):
        return {
            'ok': True,
            'message': '',
            'needs_rehash': not is_hashed(gespeichertes_pw),
        }

    return {
        'ok': False,
        'message': 'Falsches Passwort. Bitte erneut eingeben:',
        'needs_rehash': False,
    }


def delete_user_result(*, users, username, current_user):
    """Validiert und bereitet das Löschen eines Benutzers vor.

    Löscht hier noch nichts selbst - der Aufrufer wendet das Ergebnis an
    (damit z.B. app.current_user korrekt zurückgesetzt werden kann, bevor
    gespeichert wird).
    """
    if username not in users:
        return {
            'ok': False,
            'message': f'Benutzer "{username}" existiert nicht.',
        }

    if len(users) <= 1:
        return {
            'ok': False,
            'message': 'Der letzte verbleibende Benutzer kann nicht gelöscht werden.',
        }

    return {
        'ok': True,
        'username': username,
        'clears_current_user': username == current_user,
        'message': f'Benutzer "{username}" wurde gelöscht.',
    }


def create_user_result(*, users, username_text, password_text, settings):
    """Validiert die Eingaben und bereitet einen neuen Benutzer vor."""
    username = (username_text or '').strip()
    password = (password_text or '').strip()

    if not username:
        return {
            'ok': False,
            'message': 'Benutzername darf nicht leer sein. Bitte eingeben:',
        }

    if username in users:
        return {
            'ok': False,
            'message': 'Benutzername existiert bereits. Bitte anderen Namen wählen:',
        }

    user_data = build_default_user(
        username=username,
        password=hash_secret(password) if password else '',
        patient_name=username,
        patient_geburt='-',
        settings=settings,
    )

    return {
        'ok': True,
        'username': username,
        'user_data': user_data,
        'message': '',
    }