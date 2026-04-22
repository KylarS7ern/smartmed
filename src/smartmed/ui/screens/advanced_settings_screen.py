from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

from smartmed.hardware.slot_config import get_slot_label
from smartmed.ui.navigation import go_to_settings_menu
from smartmed.services.admin_pin_service import (
    build_admin_pin_status_text,
    build_admin_pin_update,
)


class AdvancedSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Erweiterte Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        info = Label(
            text=(
                'Hier komen später globale Einstellungen hin,\n'
                'z.B. WLAN, Zeitsynchronisation, Backup/Restore, '
                'Fach-Medikament, Passwortscshutz ect.'
            ),
            halign='center',
            valign='middle',
            size_hint=(1, 0.25)
        )
        info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        self.pin_info_label = Label(
            text='(Passwortschutz noch nicht implementiert)',
            halign='center',
            valign='middle',
            size_hint=(1, 0.1)
        )
        self.pin_info_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        self.hardware_test_label = Label(
            text='Hardware-Test noch nicht ausgeführt.',
            halign='center',
            valign='middle',
            size_hint=(1, 0.1)
        )
        self.hardware_test_label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', val)
        )

        pin_layout1 = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_pin = Label(
            text='Neuer Admin-PIN:',
            size_hint=(0.5, 0.1)
        )
        self.pin_input = TextInput(
            multiline=False,
            password=True,
            size_hint=(0.5, 1)
        )
        pin_layout1.add_widget(lbl_pin)
        pin_layout1.add_widget(self.pin_input)

        pin_layout2 = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_pin2 = Label(
            text='PIN wiederholen:',
            size_hint=(0.5, 1)
        )
        self.pin_repeat_input = TextInput(
            multiline=False,
            password=True,
            size_hint=(0.5, 1)
        )
        pin_layout2.add_widget(lbl_pin2)
        pin_layout2.add_widget(self.pin_repeat_input)

        btn_save_pin = Button(
            text='Admin-PIN speichern / entfernen',
            size_hint=(1, 0.15)
        )
        btn_save_pin.bind(on_press=self.speichern_pin)

        btn_test_fach_1 = Button(
            text=f'Hardware-Test: {get_slot_label(1)} einmal ausgeben',
            size_hint=(1, 0.12)
        )
        btn_test_fach_1.bind(on_press=self.hardware_test_fach_1)

        btn_test_fach_2 = Button(
            text=f'Hardware-Test: {get_slot_label(2)} einmal ausgeben',
            size_hint=(1, 0.12)
        )
        btn_test_fach_2.bind(on_press=self.hardware_test_fach_2)

        btn_test_fach_3 = Button(
            text=f'Hardware-Test: {get_slot_label(3)} einmal ausgeben',
            size_hint=(1, 0.12)
        )
        btn_test_fach_3.bind(on_press=self.hardware_test_fach_3)

        self.hardware_test_buttons = [
            btn_test_fach_1,
            btn_test_fach_2,
            btn_test_fach_3,
        ]

        btn_back = Button(
            text='Zurück',
            size_hint=(1, 0.15)
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(titel)
        layout.add_widget(info)
        layout.add_widget(self.pin_info_label)
        layout.add_widget(self.hardware_test_label)
        layout.add_widget(pin_layout1)
        layout.add_widget(pin_layout2)
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

    def hardware_test_fach(self, fach: int):
        self.hardware_test_label.text = (
            f'Hardware-Test für Fach {fach} startet in 1 Sekunde...'
        )
        Clock.schedule_once(
            lambda dt: self._starte_hardware_test(fach),
            1.0
        )

    def _starte_hardware_test(self, fach: int):
        app = App.get_running_app()
        result = app.fuehre_hardware_test_aus(fach=fach, anzahl=1)
        self.hardware_test_label.text = result.get(
            'message',
            'Unbekanntes Ergebnis beim Hardware-Test.'
        )
        
    def hardware_test_fach_1(self, instance):
        self.hardware_test_fach(1)

    def hardware_test_fach_2(self, instance):
        self.hardware_test_fach(2)

    def hardware_test_fach_3(self, instance):
        self.hardware_test_fach(3)

    def zurueck(self, instance):
        app = App.get_running_app()
        go_to_settings_menu(app)