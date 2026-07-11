from threading import Thread

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from smartmed.hardware.slot_config import get_slot_label
from smartmed.ui import theme
from smartmed.ui.navigation import go_to_settings_menu
from smartmed.ui.widgets import (
    MutedLabel,
    SecondaryButton,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    WarningButton,
    field_row,
)
from smartmed.services.admin_pin_service import (
    build_admin_pin_status_text,
    build_admin_pin_update,
)


class AdvancedSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Erweiterte Einstellungen',
            font_size=theme.FONT_XLARGE,
            size_hint=(1, None),
            height=dp(48)
        )

        info = MutedLabel(
            text=(
                'Hier kommen später weitere globale Einstellungen hin,\n'
                'z.B. WLAN, Zeitsynchronisation, Backup/Restore, '
                'Fach-Medikament.'
            ),
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(70)
        )

        self.pin_info_label = MutedLabel(
            text='',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(36)
        )

        self.hardware_test_label = MutedLabel(
            text='Hardware-Test noch nicht ausgeführt.',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(36)
        )

        self.pin_input = StyledTextInput(
            multiline=False,
            password=True,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )
        self.pin_repeat_input = StyledTextInput(
            multiline=False,
            password=True,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        btn_save_pin = SuccessButton(
            text='Admin-PIN speichern / entfernen',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_save_pin.bind(on_press=self.speichern_pin)

        btn_test_fach_1 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(1)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_1.bind(on_press=self.hardware_test_fach_1)

        btn_test_fach_2 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(2)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_2.bind(on_press=self.hardware_test_fach_2)

        btn_test_fach_3 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(3)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_3.bind(on_press=self.hardware_test_fach_3)

        self.hardware_test_buttons = [
            btn_test_fach_1,
            btn_test_fach_2,
            btn_test_fach_3,
        ]

        btn_back = SecondaryButton(
            text='Zurück',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(titel)
        layout.add_widget(info)
        layout.add_widget(self.pin_info_label)
        layout.add_widget(self.hardware_test_label)
        layout.add_widget(field_row('Neuer Admin-PIN:', self.pin_input))
        layout.add_widget(field_row('PIN wiederholen:', self.pin_repeat_input))
        layout.add_widget(btn_save_pin)
        layout.add_widget(btn_test_fach_1)
        layout.add_widget(btn_test_fach_2)
        layout.add_widget(btn_test_fach_3)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        """Status anzeigen, wenn Screen geöffnet wird."""
        app = App.get_running_app()
        self.pin_info_label.text = build_admin_pin_status_text(
            getattr(app, 'admin_pin', '')
        )
        self.pin_input.text = ''
        self.pin_repeat_input.text = ''
        self.hardware_test_label.text = 'Hardware-Test noch nicht ausgeführt.'
        self._set_hardware_test_buttons_enabled(True)

    def speichern_pin(self, instance):
        """Admin-PIN speichern oder entfernen."""
        app = App.get_running_app()

        result = build_admin_pin_update(
            self.pin_input.text,
            self.pin_repeat_input.text,
        )

        if not result['ok']:
            self.pin_info_label.text = result['message']
            return

        app.admin_pin = result['admin_pin']
        app.save_data()
        self.pin_info_label.text = result['message']

    def _set_hardware_test_buttons_enabled(self, enabled: bool):
        for button in self.hardware_test_buttons:
            button.disabled = not enabled

    def hardware_test_fach(self, fach: int):
        self._set_hardware_test_buttons_enabled(False)
        self.hardware_test_label.text = (
            f'Hardware-Test für {get_slot_label(fach)} startet in 1 Sekunde...'
        )
        Clock.schedule_once(
            lambda dt: self._starte_hardware_test_im_hintergrund(fach),
            1.0
        )

    def _starte_hardware_test_im_hintergrund(self, fach: int):
        # Eine echte Ausgabe lässt den Arduino mehrere Sekunden am Motor
        # drehen, bevor er antwortet - ohne eigenen Thread würde die
        # gesamte App (Touch, Uhrzeit, Timer) für diese Zeit einfrieren.
        Thread(
            target=self._run_hardware_test_worker,
            args=(fach,),
            daemon=True,
        ).start()

    def _run_hardware_test_worker(self, fach: int):
        try:
            app = App.get_running_app()
            result = app.fuehre_hardware_test_aus(fach=fach, anzahl=1)
        except Exception as exc:
            result = {
                'message': f'Unerwarteter Fehler beim Hardware-Test: {exc}'
            }

        Clock.schedule_once(
            lambda dt: self._verarbeite_hardware_test_ergebnis(result),
            0
        )

    def _verarbeite_hardware_test_ergebnis(self, result: dict):
        self.hardware_test_label.text = result.get(
            'message',
            'Unbekanntes Ergebnis beim Hardware-Test.'
        )
        self._set_hardware_test_buttons_enabled(True)

    def hardware_test_fach_1(self, instance):
        self.hardware_test_fach(1)

    def hardware_test_fach_2(self, instance):
        self.hardware_test_fach(2)

    def hardware_test_fach_3(self, instance):
        self.hardware_test_fach(3)

    def zurueck(self, instance):
        app = App.get_running_app()
        go_to_settings_menu(app)
