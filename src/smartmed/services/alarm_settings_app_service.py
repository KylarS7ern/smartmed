from smartmed.services.alarm_settings_service import (
    build_alarm_settings_form_data,
    build_alarm_settings_update,
    resolve_email_for_recipient_choice,
)


def build_alarm_settings_screen_data(app) -> dict:
    """Bereitet die aktuellen Alarm-Einstellungen aus der App für das UI auf."""
    settings = getattr(app, "settings", {}) or {}
    return build_alarm_settings_form_data(settings)


def resolve_alarm_email_for_app(app, recipient_choice: str, current_email: str) -> str:
    """Löst die Empfänger-Auswahl gegen die in der App hinterlegten E-Mail-Adressen auf."""
    return resolve_email_for_recipient_choice(
        recipient_choice,
        doctor_email=getattr(app, "doctor_email", ""),
        contact1_email=getattr(app, "contact1_email", ""),
        contact2_email=getattr(app, "contact2_email", ""),
        current_email=current_email,
    )


def save_alarm_settings_from_form(
    app,
    *,
    alarm_delay_text: str,
    alarm_mode_text: str,
    notify_text: str,
    email_to_text: str,
    telegram_chat_id_text: str,
    email_recipient_text: str,
) -> dict:
    """Übernimmt Formularwerte ins App-Settings-Dictionary und speichert sie."""
    if getattr(app, "settings", None) is None:
        app.settings = {}

    result = build_alarm_settings_update(
        alarm_delay_text=alarm_delay_text,
        alarm_mode_text=alarm_mode_text,
        notify_text=notify_text,
        email_to_text=email_to_text,
        telegram_chat_id_text=telegram_chat_id_text,
        email_recipient_text=email_recipient_text,
    )

    app.settings.update(result["settings_update"])
    app.save_data()
    return result


def send_alarm_test_notification(app) -> None:
    """Löst eine Test-Benachrichtigung über die bestehende Alarmfunktion der App aus."""
    dummy_eintrag = {
        "tag": "Mo",
        "zeit": "12:00",
        "fach": "1",
        "medikament": "Test-Medikament",
        "anzahl": 1,
    }
    app.sende_alarm_benachrichtigungen(dummy_eintrag)