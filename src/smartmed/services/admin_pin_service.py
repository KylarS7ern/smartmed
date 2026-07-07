from smartmed.services.security_service import hash_secret, is_hashed, verify_secret


def has_admin_pin(admin_pin):
    """Prüft, ob überhaupt ein Admin-PIN gesetzt ist."""
    return bool((admin_pin or '').strip())


def build_admin_pin_status_text(admin_pin):
    """Text für den aktuellen PIN-Status im UI."""
    if has_admin_pin(admin_pin):
        return 'Aktueller Status: PIN ist gesetzt'
    return 'Aktueller Status: Kein PIN gesetzt'


def verify_admin_pin(admin_pin, entered_pin_text):
    """Prüft eine eingegebene PIN gegen die gespeicherte (gehashte oder alte Klartext-) PIN."""
    gespeicherte_pin = (admin_pin or '').strip()
    eingegebene_pin = (entered_pin_text or '').strip()

    if not gespeicherte_pin:
        return {
            'ok': True,
            'message': '',
            'needs_rehash': False,
        }

    if verify_secret(gespeicherte_pin, eingegebene_pin):
        return {
            'ok': True,
            'message': '',
            'needs_rehash': not is_hashed(gespeicherte_pin),
        }

    return {
        'ok': False,
        'message': 'Falscher PIN. Bitte erneut eingeben:',
        'needs_rehash': False,
    }


def build_admin_pin_update(pin1_text, pin2_text):
    """Validiert neue PIN-Eingaben und bereitet das (gehashte) Update vor."""
    pin1 = (pin1_text or '').strip()
    pin2 = (pin2_text or '').strip()

    if not pin1 and not pin2:
        return {
            'ok': True,
            'admin_pin': '',
            'message': 'PIN-Schutz wurde deaktiviert.',
        }

    if pin1 != pin2:
        return {
            'ok': False,
            'admin_pin': None,
            'message': 'Die eingegebenen PINs stimmen nicht überein.',
        }

    if len(pin1) < 4:
        return {
            'ok': False,
            'admin_pin': None,
            'message': 'PIN muss mindestens 4 Zeichen lang sein.',
        }

    return {
        'ok': True,
        'admin_pin': hash_secret(pin1),
        'message': 'Admin-PIN wurde gespeichert.',
    }
