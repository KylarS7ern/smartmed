from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

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

        btn_back = Button(
            text='Zurück',
            size_hint=(1, 0.15)
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(titel)
        layout.add_widget(info)
        layout.add_widget(self.pin_info_label)
        layout.add_widget(pin_layout1)
        layout.add_widget(pin_layout2)
        layout.add_widget(btn_save_pin)
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
        
    def zurueck(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'
