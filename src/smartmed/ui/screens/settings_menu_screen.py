from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from smartmed.services.admin_pin_service import (
    has_admin_pin,
    verify_admin_pin,
)
from smartmed.services.security_service import hash_secret

from smartmed.ui import theme
from smartmed.ui.navigation import (
    go_to_menu,
    go_to_settings,
    go_to_settings_advanced,
    go_to_settings_patient,
)
from smartmed.ui.widgets import (
    BodyLabel,
    PrimaryButton,
    SecondaryButton,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    make_popup,
)


class SettingsMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Einstellungen',
            size_hint=(1, 0.18)
        )

        btn_kwargs = dict(font_size=theme.FONT_LARGE, size_hint=(1, 0.18))

        btn_patient = PrimaryButton(text='Patienten-Einstellungen', **btn_kwargs)
        btn_alarm = PrimaryButton(text='Alarm-Einstellungen', **btn_kwargs)
        btn_advanced = PrimaryButton(text='Erweiterte Einstellungen', **btn_kwargs)
        btn_back = SecondaryButton(text='Zurück zum Hauptmenü', **btn_kwargs)

        btn_patient.bind(on_press=self.zeige_patient)
        btn_alarm.bind(on_press=self.zeige_alarm)
        btn_advanced.bind(on_press=self.zeige_erweitert)
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(btn_patient)
        layout.add_widget(btn_alarm)
        layout.add_widget(btn_advanced)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def zeige_patient(self, instance):
        self._check_admin_pin_and_open('settings_patient')

    def zeige_alarm(self, instance):
        self._check_admin_pin_and_open('settings')

    def zeige_erweitert(self, instance):
        self._check_admin_pin_and_open('settings_advanced')

    def _open_target_screen(self, app, target_screen_name):
        """Öffnet den gewünschten Settings-Screen."""
        if target_screen_name == 'settings':
            go_to_settings(app)
        elif target_screen_name == 'settings_advanced':
            go_to_settings_advanced(app)
        elif target_screen_name == 'settings_patient':
            go_to_settings_patient(app)

    def _check_admin_pin_and_open(self, target_screen_name):
        """Prüfen, ob Admin-PIN gesetzt ist und ggf. abfragen."""
        app = App.get_running_app()
        pin = getattr(app, 'admin_pin', '')

        if not has_admin_pin(pin):
            self._open_target_screen(app, target_screen_name)
            return

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text='Bitte Admin-PIN eingeben:',
            halign='center',
            valign='middle'
        )

        pin_input = StyledTextInput(
            multiline=False,
            password=True,
            size_hint=(1, 0.4)
        )

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, 0.3)
        )
        btn_ok = SuccessButton(text='OK')
        btn_cancel = SecondaryButton(text='Abbrechen')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(label)
        layout.add_widget(pin_input)
        layout.add_widget(btn_layout)

        popup = make_popup(title='PIN-Schutz', content=layout, size_hint=(0.8, 0.5))

        def on_ok(_inst):
            result = verify_admin_pin(pin, pin_input.text)

            if result['ok']:
                if result.get('needs_rehash'):
                    app.admin_pin = hash_secret(pin_input.text.strip())
                    app.save_data()
                popup.dismiss()
                self._open_target_screen(app, target_screen_name)
            else:
                label.text = result['message']

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)
