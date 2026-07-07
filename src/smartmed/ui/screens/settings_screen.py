from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from smartmed.ui import theme
from smartmed.ui.navigation import go_to_settings_menu
from smartmed.ui.widgets import (
    BodyLabel,
    PrimaryButton,
    SecondaryButton,
    StyledSpinner,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    field_row,
    make_popup,
)
from smartmed.services.alarm_settings_app_service import (
    build_alarm_settings_screen_data,
    resolve_alarm_email_for_app,
    save_alarm_settings_from_form,
    send_alarm_test_notification,
)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )

        titel = TitleLabel(
            text='Alarm-Einstellungen',
            font_size=theme.FONT_XLARGE,
        )

        btn_info = PrimaryButton(
            text='!',
            size_hint=(0.2, 1)
        )
        btn_info.bind(on_press=self.zeige_info_popup)

        titel_layout.add_widget(titel)
        titel_layout.add_widget(btn_info)

        self.alarm_delay_input = StyledTextInput(
            multiline=False,
            input_filter='int',
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        self.alarm_mode_spinner = StyledSpinner(
            text='Popup + Log',
            values=('Popup + Log', 'Nur Log'),
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        self.notify_spinner = StyledSpinner(
            text='Nichts',
            values=('Nichts', 'Nur E-Mail', 'Nur Telegram', 'E-Mail + Telegram'),
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        self.email_recipients_spinner = StyledSpinner(
            text='Manuell',
            values=('Manuell', 'Arzt', 'Kontakt 1', 'Kontakt 2'),
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )
        self.email_recipients_spinner.bind(text=self.on_email_recipient_changed)

        self.email_to_input = StyledTextInput(
            multiline=False,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        self.telegram_chat_id_input = StyledTextInput(
            multiline=False,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        btn_test = PrimaryButton(
            text='Testnachricht senden',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test.bind(on_press=self.sende_testnachricht)

        btn_speichern = SuccessButton(
            text='Einstellungen speichern',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_speichern.bind(on_press=self.speichern_einstellungen)

        btn_back = SecondaryButton(
            text='Zurück zum Hauptmenü',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel_layout)
        layout.add_widget(field_row('Zeit bis Alarm (Min.):', self.alarm_delay_input))
        layout.add_widget(field_row('Art des Alarms:', self.alarm_mode_spinner))
        layout.add_widget(field_row('Benachrichtigung:', self.notify_spinner))
        layout.add_widget(field_row('Empfänger wählen:', self.email_recipients_spinner))
        layout.add_widget(field_row('E-Mail Empfänger:', self.email_to_input))
        layout.add_widget(field_row('Telegram Chat-ID:', self.telegram_chat_id_input))
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_test)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    @staticmethod
    def _app():
        return App.get_running_app()

    def on_pre_enter(self, *args):
        """Aktuelle Einstellungen ins UI laden, wenn Screen angezeigt wird."""
        form_data = build_alarm_settings_screen_data(self._app())

        self.alarm_delay_input.text = form_data['alarm_delay_text']
        self.alarm_mode_spinner.text = form_data['alarm_mode_text']
        self.notify_spinner.text = form_data['notify_text']
        self.email_recipients_spinner.text = form_data['email_recipient_text']
        self.email_to_input.text = form_data['email_to']
        self.telegram_chat_id_input.text = form_data['telegram_chat_id']

    def zeige_info_popup(self, instance):
        """Zeigt die ausführliche Anleitung zur Benachrichtigung als Popup an."""
        info_text = (
            'Benachrichtigungen einrichten:\n\n'
            '1) E-Mail:\n'
            "   - Unten im Feld \"E-Mail Empfänger\" die Adresse der\n"
            "     Kontaktperson eintragen (z.B. mutter@example.com).\n"
            "   - Auf dem Handy der Kontaktperson muss eine Mail-App\n"
            "     eingerichtet sein, damit eine Push-Nachricht erscheint.\n\n"
            "2) Telegram:\n"
            "   - Auf dem Handy die Telegram-App öffnen.\n"
            "   - Den SmartMedSpender-Bot suchen (z.B. @SmartMedSpenderBot)\n"
            "     und auf \"Start\" tippen.\n"
            "   - Die Telegram-Chat-ID wird normalerweise vom Betreuer/\n"
            "     Techniker ermittelt und hier im Feld \"Telegram Chat-ID\"\n"
            "     eingetragen.\n\n"
            "3) Oben unter \"Benachrichtigung\" auswählen, ob nichts,\n"
            "   nur E-Mail, nur Telegram oder beides verwendet werden soll.\n\n"
            "4) Mit \"Testnachricht senden\" können Sie prüfen,\n"
            '   ob alles klappt.'
        )

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=info_text,
            font_size=theme.FONT_SMALL,
            halign='left',
            valign='top'
        )

        btn_ok = PrimaryButton(
            text='Schliessen',
            size_hint=(1, 0.2)
        )

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup = make_popup(title='Hilfe zu Benachrichtigungen', content=layout, size_hint=(0.9, 0.8))

        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def on_email_recipient_changed(self, spinner, value):
        """Wenn Empfänger-Auswahl geändert wird, passende Adresse einsetzen."""
        self.email_to_input.text = resolve_alarm_email_for_app(
            self._app(),
            recipient_choice=value,
            current_email=self.email_to_input.text,
        )

    def sende_testnachricht(self, instance):
        app = self._app()
        self.speichern_einstellungen(instance)
        send_alarm_test_notification(app)

    def speichern_einstellungen(self, instance):
        app = self._app()

        result = save_alarm_settings_from_form(
            app,
            alarm_delay_text=self.alarm_delay_input.text,
            alarm_mode_text=self.alarm_mode_spinner.text,
            notify_text=self.notify_spinner.text,
            email_to_text=self.email_to_input.text,
            telegram_chat_id_text=self.telegram_chat_id_input.text,
            email_recipient_text=self.email_recipients_spinner.text,
        )

        if result['warning']:
            print(result['warning'])

        print('Alarm-Einstellungen gespeichert:', app.settings)

    def zurueck_zum_menue(self, instance):
        go_to_settings_menu(self._app())
