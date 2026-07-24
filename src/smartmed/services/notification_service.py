from email.message import EmailMessage

from smartmed.config import (
    TELEGRAM_BOT_TOKEN,
    EMAIL_SMTP_SERVER,
    EMAIL_SMTP_PORT,
    EMAIL_USERNAME,
    EMAIL_PASSWORT,
)

import smtplib
import time
import requests

# Alarm-Benachrichtigungen sind sicherheitsrelevant (verpasste Einnahme) und
# laufen unbeaufsichtigt - ein einzelner Netzwerk-Hänger soll die
# Benachrichtigung nicht stillschweigend ausfallen lassen. Deshalb hier ein
# automatischer, kurzer Retry statt nur eines manuellen "Erneut senden".
_ALARM_SEND_VERSUCHE = 2
_ALARM_RETRY_VERZOEGERUNG_S = 3.0


def build_alarm_text(eintrag: dict) -> str:
    tag = eintrag.get("tag", "")
    zeit = eintrag.get("zeit", "")
    fach = eintrag.get("fach", "")
    med = eintrag.get("medikament", "")
    anzahl = eintrag.get("anzahl", 1)

    return (
        "Alarm: Einnahme NICHT bestätigt:\n"
        f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
    )


def build_late_confirmation_text(eintrag: dict) -> str:
    tag = eintrag.get("tag", "")
    zeit = eintrag.get("zeit", "")
    fach = eintrag.get("fach", "")
    med = eintrag.get("medikament", "")
    anzahl = eintrag.get("anzahl", 1)

    return (
        "Information: Einnahme wurde nachträglich bestätigt "
        "(nachdem bereits ein Alarm ausgelöst wurde):\n"
        f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
    )


def send_telegram_alarm(
    *,
    bot_token: str,
    chat_id: str,
    text: str,
    log_callback=None,
) -> None:
    if not bot_token or not chat_id:
        print("Telegram nicht konfiguriert (Token oder Chat-ID fehlt).")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    letzter_fehler = None

    for versuch in range(1, _ALARM_SEND_VERSUCHE + 1):
        try:
            resp = requests.post(url, data={"chat_id": chat_id, "text": text})
            if resp.status_code == 200:
                print("Telegram-Alarm gesendet.")
                if log_callback:
                    log_callback("Telegram-Alarm gesendet.")
                return
            letzter_fehler = f"Fehler beim Telegram-Request: {resp.text}"
        except Exception as e:
            letzter_fehler = f"Fehler beim Senden von Telegram: {e}"

        if versuch < _ALARM_SEND_VERSUCHE:
            time.sleep(_ALARM_RETRY_VERZOEGERUNG_S)

    print(letzter_fehler)
    if log_callback:
        log_callback(f"{letzter_fehler} (auch nach Wiederholungsversuch fehlgeschlagen)")


def send_email_alarm(
    *,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_addr: str,
    subject: str,
    body: str,
    log_callback=None,
) -> None:
    if not username or not password:
        print("E-Mail nicht konfiguriert (Username/Passwort fehlt im Code).")
        return

    if not to_addr:
        print("Keine Empfänger-Adresse (email_to) in den Einstellungen.")
        return

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    letzter_fehler = None

    for versuch in range(1, _ALARM_SEND_VERSUCHE + 1):
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(username, password)
                smtp.send_message(msg)
            print("Alarm-E-Mail gesendet.")
            if log_callback:
                log_callback(f"E-Mail-Alarm an {to_addr} gesendet.")
            return
        except Exception as e:
            letzter_fehler = str(e)

        if versuch < _ALARM_SEND_VERSUCHE:
            time.sleep(_ALARM_RETRY_VERZOEGERUNG_S)

    print("Fehler beim Senden der E-Mail:", letzter_fehler)
    if log_callback:
        log_callback(
            f"Fehler beim Senden der E-Mail: {letzter_fehler} "
            "(auch nach Wiederholungsversuch fehlgeschlagen)"
        )


def send_email_with_attachment(
    *,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_addr: str,
    subject: str,
    body: str,
    attachment_text: str,
    attachment_filename: str,
    log_callback=None,
) -> dict:
    """Sendet eine E-Mail mit einem Text-Anhang.

    Anders als send_email_alarm() gibt diese Funktion ein Ergebnis zurück,
    damit der Aufrufer (z.B. ein manueller "Log senden"-Button) dem Benutzer
    sofort eine Erfolgs-/Fehlermeldung anzeigen kann.
    """
    if not username or not password:
        message = "E-Mail nicht konfiguriert (Benutzername/Passwort fehlt)."
        if log_callback:
            log_callback(message)
        return {"ok": False, "message": message}

    if not to_addr:
        message = "Keine Empfänger-Adresse hinterlegt (siehe Alarm-Einstellungen)."
        if log_callback:
            log_callback(message)
        return {"ok": False, "message": message}

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_attachment(
        attachment_text.encode("utf-8"),
        maintype="text",
        subtype="plain",
        filename=attachment_filename,
    )

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        message = f"E-Mail mit Anhang an {to_addr} gesendet."
        if log_callback:
            log_callback(message)
        return {"ok": True, "message": message}
    except Exception as e:
        message = f"Fehler beim Senden der E-Mail: {e}"
        if log_callback:
            log_callback(message)
        return {"ok": False, "message": message}


def send_log_export_email(*, log_text: str, to_addr: str, log_callback=None) -> dict:
    """Versendet das Ereignisprotokoll per E-Mail (als Anhang) über denselben
    Account, der auch Alarm-Benachrichtigungen verschickt."""
    return send_email_with_attachment(
        smtp_server=EMAIL_SMTP_SERVER,
        smtp_port=EMAIL_SMTP_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORT,
        to_addr=to_addr,
        subject="SmartMedSpender-Ereignisprotokoll",
        body="Im Anhang befindet sich das aktuelle Ereignisprotokoll.",
        attachment_text=log_text,
        attachment_filename="smartmed_log.txt",
        log_callback=log_callback,
    )


def send_backup_export_email(*, backup_text: str, to_addr: str, log_callback=None) -> dict:
    """Versendet eine vollständige Datensicherung per E-Mail (als Anhang) über
    denselben Account, der auch Alarm-Benachrichtigungen verschickt."""
    return send_email_with_attachment(
        smtp_server=EMAIL_SMTP_SERVER,
        smtp_port=EMAIL_SMTP_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORT,
        to_addr=to_addr,
        subject="SmartMedSpender-Datensicherung",
        body=(
            "Im Anhang befindet sich eine vollständige Datensicherung "
            "(alle Benutzer, Einnahmepläne, Logs). Diese Datei kann über "
            "'Sicherung wiederherstellen' in den erweiterten Einstellungen "
            "wieder eingespielt werden."
        ),
        attachment_text=backup_text,
        attachment_filename="smartmed_backup.json",
        log_callback=log_callback,
    )


def _send_text_notifications(
    *,
    text: str,
    subject: str,
    notify_mode: str,
    email_to: str,
    telegram_chat_id: str,
    telegram_bot_token: str,
    email_smtp_server: str,
    email_smtp_port: int,
    email_username: str,
    email_password: str,
    log_callback=None,
) -> None:
    if notify_mode in ("email", "both"):
        send_email_alarm(
            smtp_server=email_smtp_server,
            smtp_port=email_smtp_port,
            username=email_username,
            password=email_password,
            to_addr=email_to,
            subject=subject,
            body=text,
            log_callback=log_callback,
        )

    if notify_mode in ("telegram", "both"):
        send_telegram_alarm(
            bot_token=telegram_bot_token,
            chat_id=telegram_chat_id,
            text=text,
            log_callback=log_callback,
        )


def send_alarm_notifications(
    *,
    eintrag: dict,
    notify_mode: str,
    email_to: str,
    telegram_chat_id: str,
    telegram_bot_token: str,
    email_smtp_server: str,
    email_smtp_port: int,
    email_username: str,
    email_password: str,
    log_callback=None,
) -> None:
    _send_text_notifications(
        text=build_alarm_text(eintrag),
        subject="SmartMedSpender-Alarm",
        notify_mode=notify_mode,
        email_to=email_to,
        telegram_chat_id=telegram_chat_id,
        telegram_bot_token=telegram_bot_token,
        email_smtp_server=email_smtp_server,
        email_smtp_port=email_smtp_port,
        email_username=email_username,
        email_password=email_password,
        log_callback=log_callback,
    )


def send_late_confirmation_notifications(
    *,
    eintrag: dict,
    notify_mode: str,
    email_to: str,
    telegram_chat_id: str,
    telegram_bot_token: str,
    email_smtp_server: str,
    email_smtp_port: int,
    email_username: str,
    email_password: str,
    log_callback=None,
) -> None:
    """Zweite Benachrichtigung, wenn eine Einnahme erst nach dem Alarm bestätigt wurde."""
    _send_text_notifications(
        text=build_late_confirmation_text(eintrag),
        subject="SmartMedSpender-Nachträgliche Bestätigung",
        notify_mode=notify_mode,
        email_to=email_to,
        telegram_chat_id=telegram_chat_id,
        telegram_bot_token=telegram_bot_token,
        email_smtp_server=email_smtp_server,
        email_smtp_port=email_smtp_port,
        email_username=email_username,
        email_password=email_password,
        log_callback=log_callback,
    )


def send_alarm_notifications_for_settings(
    *,
    eintrag: dict,
    settings: dict,
    log_callback=None,
) -> None:
    """Liest die Alarm-Einstellungen aus settings und ruft den generischen Versand auf."""
    send_alarm_notifications(
        eintrag=eintrag,
        notify_mode=settings.get("notify_mode", "none"),
        email_to=settings.get("email_to", "").strip(),
        telegram_chat_id=settings.get("telegram_chat_id", "").strip(),
        telegram_bot_token=TELEGRAM_BOT_TOKEN,
        email_smtp_server=EMAIL_SMTP_SERVER,
        email_smtp_port=EMAIL_SMTP_PORT,
        email_username=EMAIL_USERNAME,
        email_password=EMAIL_PASSWORT,
        log_callback=log_callback,
    )


def send_late_confirmation_notifications_for_settings(
    *,
    eintrag: dict,
    settings: dict,
    log_callback=None,
) -> None:
    """Liest die Alarm-Einstellungen aus settings und sendet die Nachbestätigung."""
    send_late_confirmation_notifications(
        eintrag=eintrag,
        notify_mode=settings.get("notify_mode", "none"),
        email_to=settings.get("email_to", "").strip(),
        telegram_chat_id=settings.get("telegram_chat_id", "").strip(),
        telegram_bot_token=TELEGRAM_BOT_TOKEN,
        email_smtp_server=EMAIL_SMTP_SERVER,
        email_smtp_port=EMAIL_SMTP_PORT,
        email_username=EMAIL_USERNAME,
        email_password=EMAIL_PASSWORT,
        log_callback=log_callback,
    )
