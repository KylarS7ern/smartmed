from email.message import EmailMessage
import smtplib
import requests


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

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        resp = requests.post(url, data={"chat_id": chat_id, "text": text})
        if resp.status_code == 200:
            print("Telegram-Alarm gesendet.")
            if log_callback:
                log_callback("Telegram-Alarm gesendet.")
        else:
            print("Fehler beim Telegram-Request:", resp.text)
            if log_callback:
                log_callback(f"Fehler beim Telegram-Request: {resp.text}")
    except Exception as e:
        print("Fehler beim Senden von Telegram:", e)
        if log_callback:
            log_callback(f"Fehler beim Senden von Telegram: {e}")


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

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        print("Alarm-E-Mail gesendet.")
        if log_callback:
            log_callback(f"E-Mail-Alarm an {to_addr} gesendet.")
    except Exception as e:
        print("Fehler beim Senden der E-Mail:", e)
        if log_callback:
            log_callback(f"Fehler beim Senden der E-Mail: {e}")


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
    text = build_alarm_text(eintrag)

    if notify_mode in ("email", "both"):
        send_email_alarm(
            smtp_server=email_smtp_server,
            smtp_port=email_smtp_port,
            username=email_username,
            password=email_password,
            to_addr=email_to,
            subject="SmartMedSpender-Alarm",
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