from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from smartmed.services.alarm_settings_service import (
    build_alarm_settings_form_data,
    build_alarm_settings_update,
    resolve_email_for_recipient_choice,
)

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )

        titel = Label(
            text='Alarm-Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        btn_info = Button(
            text='!',
            size_hint=(0.2, 1)
        )
        btn_info.bind(on_press=self.zeige_info_popup)

        titel_layout.add_widget(titel)
        titel_layout.add_widget(btn_info)

        alarm_delay_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_delay = Label(
            text='Zeit bis Alarm (Minuten):',
            size_hint=(0.6, 1)
        )
        self.alarm_delay_input = TextInput(
            multiline=False,
            input_filter='int',
            size_hint=(0.4, 1)
        )
        alarm_delay_layout.add_widget(lbl_delay)
        alarm_delay_layout.add_widget(self.alarm_delay_input)

        alarm_mode_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_mode = Label(
            text='Art des Alarms:',
            size_hint=(0.6, 1)
        )
        self.alarm_mode_spinner = Spinner(
            text='Popup + Log',
            values=('Popup + Log', 'Nur Log'),
            size_hint=(0.4, 1)
        )
        alarm_mode_layout.add_widget(lbl_mode)
        alarm_mode_layout.add_widget(self.alarm_mode_spinner)

        notify_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_notify = Label(
            text='Benachrichtigung:',
            size_hint=(0.6, 1)
        )
        self.notify_spinner = Spinner(
            text='Nichts',
            values=('Nichts', 'Nur E-Mail', 'Nur Telegram', 'E-Mail + Telegram'),
            size_hint=(0.4, 1)
        )
        notify_layout.add_widget(lbl_notify)
        notify_layout.add_widget(self.notify_spinner)

        email_choice_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_email_choice = Label(
            text='Empfänger wählen:',
            size_hint=(0.6, 1)
        )
        self.email_recipients_spinner = Spinner(
            text='Manuell',
            values=('Manuell', 'Arzt', 'Kontakt 1', 'Kontakt 2'),
            size_hint=(0.4, 1)
        )
        self.email_recipients_spinner.bind(text=self.on_email_recipient_changed)

        email_choice_layout.add_widget(lbl_email_choice)
        email_choice_layout.add_widget(self.email_recipients_spinner)

        email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_email = Label(
            text='E-Mail Empfänger:',
            size_hint=(0.6, 1)
        )
        self.email_to_input = TextInput(
            multiline=False,
            size_hint=(0.4, 1)
        )
        email_layout.add_widget(lbl_email)
        email_layout.add_widget(self.email_to_input)

        telegram_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_tg = Label(
            text='Telegram Chat-ID:',
            size_hint=(0.6, 1)
        )
        self.telegram_chat_id_input = TextInput(
            multiline=False,
            size_hint=(0.4, 1)
        )
        telegram_layout.add_widget(lbl_tg)
        telegram_layout.add_widget(self.telegram_chat_id_input)

        btn_test = Button(
            text='Testnachricht senden',
            size_hint=(1, 0.15)
        )
        btn_test.bind(on_press=self.sende_testnachricht)

        btn_speichern = Button(
            text='Einstellungen speichern',
            size_hint=(1, 0.15)
        )
        btn_speichern.bind(on_press=self.speichern_einstellungen)

        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.15)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel_layout)
        layout.add_widget(alarm_delay_layout)
        layout.add_widget(alarm_mode_layout)
        layout.add_widget(notify_layout)
        layout.add_widget(email_choice_layout)
        layout.add_widget(email_layout)
        layout.add_widget(telegram_layout)
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_test)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        """Aktuelle Einstellungen ins UI laden, wenn Screen angezeigt wird."""
        app = App.get_running_app()
        form_data = build_alarm_settings_form_data(app.settings)

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

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=info_text,
            halign='left',
            valign='top'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_ok = Button(
            text='Schliessen',
            size_hint=(1, 0.2)
        )

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup = Popup(
            title='Hilfe zu Benachrichtigungen',
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )

        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def on_email_recipient_changed(self, spinner, value):
        """Wenn Empfänger-Auswahl geändert wird, passende Adresse einsetzen."""
        app = App.get_running_app()

        self.email_to_input.text = resolve_email_for_recipient_choice(
            value,
            doctor_email=getattr(app, 'doctor_email', ''),
            contact1_email=getattr(app, 'contact1_email', ''),
            contact2_email=getattr(app, 'contact2_email', ''),
            current_email=self.email_to_input.text,
        )

    def sende_testnachricht(self, instance):
        app = App.get_running_app()

        self.speichern_einstellungen(instance)

        dummy_eintrag = {
            'tag': 'Mo',
            'zeit': '12:00',
            'fach': '1',
            'medikament': 'Test-Medikament',
            'anzahl': 1,
        }
        app.sende_alarm_benachrichtigungen(dummy_eintrag)

    def speichern_einstellungen(self, instance):
        app = App.get_running_app()

        result = build_alarm_settings_update(
            alarm_delay_text=self.alarm_delay_input.text,
            alarm_mode_text=self.alarm_mode_spinner.text,
            notify_text=self.notify_spinner.text,
            email_to_text=self.email_to_input.text,
            telegram_chat_id_text=self.telegram_chat_id_input.text,
            email_recipient_text=self.email_recipients_spinner.text,
        )

        app.settings.update(result['settings_update'])
        app.save_data()

        if result['warning']:
            print(result['warning'])

        print('Alarm-Einstellungen gespeichert:', app.settings)
        
    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'
