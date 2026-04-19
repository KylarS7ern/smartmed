import unittest

from smartmed.services.alarm_settings_app_service import (
    resolve_alarm_email_for_app,
    save_alarm_settings_from_form,
    send_alarm_test_notification,
)


class DummyApp:
    def __init__(self):
        self.settings = {}
        self.doctor_email = "arzt@example.com"
        self.contact1_email = "kontakt1@example.com"
        self.contact2_email = "kontakt2@example.com"
        self.save_called = False
        self.sent_alarm_entry = None

    def save_data(self):
        self.save_called = True

    def sende_alarm_benachrichtigungen(self, eintrag):
        self.sent_alarm_entry = eintrag


class AlarmSettingsAppServiceTests(unittest.TestCase):
    def test_resolve_alarm_email_for_app_uses_selected_contact(self):
        app = DummyApp()

        result = resolve_alarm_email_for_app(
            app,
            recipient_choice="Kontakt 1",
            current_email="manuell@example.com",
        )

        self.assertEqual(result, "kontakt1@example.com")

    def test_save_alarm_settings_from_form_updates_app_and_saves(self):
        app = DummyApp()

        result = save_alarm_settings_from_form(
            app,
            alarm_delay_text="15",
            alarm_mode_text="Popup + Log",
            notify_text="Nur E-Mail",
            email_to_text="ziel@example.com",
            telegram_chat_id_text="123456",
            email_recipient_text="Manuell",
        )

        self.assertTrue(app.save_called)
        for key, value in result["settings_update"].items():
            self.assertEqual(app.settings[key], value)

    def test_send_alarm_test_notification_calls_existing_app_alarm_method(self):
        app = DummyApp()

        send_alarm_test_notification(app)

        self.assertIsNotNone(app.sent_alarm_entry)
        self.assertEqual(app.sent_alarm_entry["medikament"], "Test-Medikament")
        self.assertEqual(app.sent_alarm_entry["fach"], "1")


if __name__ == "__main__":
    unittest.main()