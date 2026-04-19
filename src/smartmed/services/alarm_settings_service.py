ALARM_MODE_TO_TEXT = {
    'popup': 'Popup + Log',
    'log': 'Nur Log',
}

TEXT_TO_ALARM_MODE = {
    'Popup + Log': 'popup',
    'Nur Log': 'log',
}

NOTIFY_MODE_TO_TEXT = {
    'none': 'Nichts',
    'email': 'Nur E-Mail',
    'telegram': 'Nur Telegram',
    'both': 'E-Mail + Telegram',
}

TEXT_TO_NOTIFY_MODE = {
    'Nichts': 'none',
    'Nur E-Mail': 'email',
    'Nur Telegram': 'telegram',
    'E-Mail + Telegram': 'both',
}

EMAIL_RECIPIENT_TO_TEXT = {
    'manual': 'Manuell',
    'doctor': 'Arzt',
    'contact1': 'Kontakt 1',
    'contact2': 'Kontakt 2',
}

TEXT_TO_EMAIL_RECIPIENT = {
    'Manuell': 'manual',
    'Arzt': 'doctor',
    'Kontakt 1': 'contact1',
    'Kontakt 2': 'contact2',
}


def build_alarm_settings_form_data(settings):
    """Bereitet interne Settings für die Anzeige im UI auf."""
    delay = settings.get('alarm_delay_min', 30)
    alarm_mode = settings.get('alarm_mode', 'popup')
    notify_mode = settings.get('notify_mode', 'none')
    email_recipient = settings.get('email_recipient', 'manual')

    return {
        'alarm_delay_text': str(delay),
        'alarm_mode_text': ALARM_MODE_TO_TEXT.get(alarm_mode, 'Popup + Log'),
        'notify_text': NOTIFY_MODE_TO_TEXT.get(notify_mode, 'Nichts'),
        'email_recipient_text': EMAIL_RECIPIENT_TO_TEXT.get(email_recipient, 'Manuell'),
        'email_to': settings.get('email_to', ''),
        'telegram_chat_id': settings.get('telegram_chat_id', ''),
    }


def build_alarm_settings_update(
    *,
    alarm_delay_text,
    alarm_mode_text,
    notify_text,
    email_to_text,
    telegram_chat_id_text,
    email_recipient_text,
):
    """Validiert und normalisiert die Alarm-Einstellungen aus dem UI."""
    warning = None

    try:
        delay = int((alarm_delay_text or '').strip() or '30')
        if delay <= 0:
            raise ValueError()
    except ValueError:
        delay = 30
        warning = 'Ungültige Alarmzeit, auf 30 Minuten gesetzt.'

    settings_update = {
        'alarm_delay_min': delay,
        'alarm_mode': TEXT_TO_ALARM_MODE.get(alarm_mode_text, 'popup'),
        'notify_mode': TEXT_TO_NOTIFY_MODE.get(notify_text, 'none'),
        'email_to': (email_to_text or '').strip(),
        'telegram_chat_id': (telegram_chat_id_text or '').strip(),
        'email_recipient': TEXT_TO_EMAIL_RECIPIENT.get(email_recipient_text, 'manual'),
    }

    return {
        'settings_update': settings_update,
        'warning': warning,
    }


def resolve_email_for_recipient_choice(
    choice_text,
    *,
    doctor_email='',
    contact1_email='',
    contact2_email='',
    current_email='',
):
    """Liefert die passende E-Mail zur UI-Auswahl."""
    if choice_text == 'Arzt':
        return (doctor_email or '').strip()

    if choice_text == 'Kontakt 1':
        return (contact1_email or '').strip()

    if choice_text == 'Kontakt 2':
        return (contact2_email or '').strip()

    return current_email