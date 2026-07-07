import unittest
from unittest.mock import MagicMock, patch

from smartmed.services.notification_service import (
    build_alarm_text,
    build_late_confirmation_text,
    send_email_with_attachment,
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


if __name__ == "__main__":
    unittest.main()
