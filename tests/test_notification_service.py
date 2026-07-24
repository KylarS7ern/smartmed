import unittest
from unittest.mock import MagicMock, patch

from smartmed.services.notification_service import (
    build_alarm_text,
    build_late_confirmation_text,
    send_email_alarm,
    send_email_with_attachment,
    send_telegram_alarm,
)


class NotificationServiceTests(unittest.TestCase):
    def test_build_alarm_text_contains_key_fields(self):
        eintrag = {"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 2}

        text = build_alarm_text(eintrag)

        self.assertIn("Mo 08:30", text)
        self.assertIn("Fach 1", text)
        self.assertIn("A (x2)", text)

    def test_build_late_confirmation_text_differs_from_alarm_text(self):
        eintrag = {"tag": "Mo", "zeit": "08:30", "fach": "1", "medikament": "A", "anzahl": 1}

        alarm_text = build_alarm_text(eintrag)
        late_text = build_late_confirmation_text(eintrag)

        self.assertNotEqual(alarm_text, late_text)
        self.assertIn("nachträglich bestätigt", late_text)
        self.assertIn("Fach 1", late_text)

    def test_send_email_with_attachment_fails_without_credentials(self):
        result = send_email_with_attachment(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="", password="",
            to_addr="empfaenger@example.com",
            subject="Test", body="Body",
            attachment_text="Loginhalt", attachment_filename="log.txt",
        )

        self.assertFalse(result["ok"])
        self.assertIn("nicht konfiguriert", result["message"])

    def test_send_email_with_attachment_fails_without_recipient(self):
        result = send_email_with_attachment(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="",
            subject="Test", body="Body",
            attachment_text="Loginhalt", attachment_filename="log.txt",
        )

        self.assertFalse(result["ok"])
        self.assertIn("Empfänger", result["message"])

    @patch("smartmed.services.notification_service.smtplib.SMTP")
    def test_send_email_with_attachment_sends_via_smtp_on_success(self, mock_smtp_cls):
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp

        result = send_email_with_attachment(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="empfaenger@example.com",
            subject="Test-Betreff", body="Test-Text",
            attachment_text="Loginhalt", attachment_filename="log.txt",
        )

        self.assertTrue(result["ok"])
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("bot@example.com", "geheim")
        mock_smtp.send_message.assert_called_once()

        gesendete_nachricht = mock_smtp.send_message.call_args[0][0]
        self.assertEqual(gesendete_nachricht["To"], "empfaenger@example.com")
        self.assertEqual(gesendete_nachricht["Subject"], "Test-Betreff")

    @patch("smartmed.services.notification_service.smtplib.SMTP")
    def test_send_email_with_attachment_reports_failure_on_smtp_error(self, mock_smtp_cls):
        mock_smtp_cls.side_effect = OSError("Verbindung fehlgeschlagen")

        result = send_email_with_attachment(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="empfaenger@example.com",
            subject="Test", body="Body",
            attachment_text="Loginhalt", attachment_filename="log.txt",
        )

        self.assertFalse(result["ok"])
        self.assertIn("Verbindung fehlgeschlagen", result["message"])

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.smtplib.SMTP")
    def test_send_email_alarm_succeeds_on_first_attempt_without_retry(self, mock_smtp_cls, mock_sleep):
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp
        log_callback = MagicMock()

        send_email_alarm(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="empfaenger@example.com",
            subject="Alarm", body="Text",
            log_callback=log_callback,
        )

        self.assertEqual(mock_smtp_cls.call_count, 1)
        mock_sleep.assert_not_called()
        log_callback.assert_called_once_with("E-Mail-Alarm an empfaenger@example.com gesendet.")

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.smtplib.SMTP")
    def test_send_email_alarm_retries_once_then_succeeds(self, mock_smtp_cls, mock_sleep):
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.side_effect = [
            OSError("kurzer Netzwerkhänger"),
            mock_smtp,
        ]

        send_email_alarm(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="empfaenger@example.com",
            subject="Alarm", body="Text",
        )

        self.assertEqual(mock_smtp_cls.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.smtplib.SMTP")
    def test_send_email_alarm_logs_failure_after_exhausting_retries(self, mock_smtp_cls, mock_sleep):
        mock_smtp_cls.return_value.__enter__.side_effect = OSError("dauerhaft nicht erreichbar")
        log_callback = MagicMock()

        send_email_alarm(
            smtp_server="smtp.gmail.com", smtp_port=587,
            username="bot@example.com", password="geheim",
            to_addr="empfaenger@example.com",
            subject="Alarm", body="Text",
            log_callback=log_callback,
        )

        self.assertEqual(mock_smtp_cls.call_count, 2)
        log_callback.assert_called_once()
        self.assertIn("Wiederholungsversuch", log_callback.call_args[0][0])

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.requests.post")
    def test_send_telegram_alarm_succeeds_on_first_attempt_without_retry(self, mock_post, mock_sleep):
        mock_post.return_value = MagicMock(status_code=200)
        log_callback = MagicMock()

        send_telegram_alarm(
            bot_token="token", chat_id="123", text="Alarm-Text", log_callback=log_callback,
        )

        self.assertEqual(mock_post.call_count, 1)
        mock_sleep.assert_not_called()
        log_callback.assert_called_once_with("Telegram-Alarm gesendet.")

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.requests.post")
    def test_send_telegram_alarm_retries_once_then_succeeds(self, mock_post, mock_sleep):
        mock_post.side_effect = [
            MagicMock(status_code=500, text="Server-Fehler"),
            MagicMock(status_code=200),
        ]

        send_telegram_alarm(bot_token="token", chat_id="123", text="Alarm-Text")

        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("smartmed.services.notification_service.time.sleep")
    @patch("smartmed.services.notification_service.requests.post")
    def test_send_telegram_alarm_logs_failure_after_exhausting_retries(self, mock_post, mock_sleep):
        mock_post.side_effect = ConnectionError("nicht erreichbar")
        log_callback = MagicMock()

        send_telegram_alarm(
            bot_token="token", chat_id="123", text="Alarm-Text", log_callback=log_callback,
        )

        self.assertEqual(mock_post.call_count, 2)
        log_callback.assert_called_once()
        self.assertIn("Wiederholungsversuch", log_callback.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
