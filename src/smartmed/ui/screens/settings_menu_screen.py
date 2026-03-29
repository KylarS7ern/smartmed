from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput


class SettingsMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.2)
        )

        btn_patient = Button(
            text='Patienten-Einstellungen',
            size_hint=(1, 0.2)
        )
        btn_alarm = Button(
            text='Alarm-Einstellungen',
            size_hint=(1, 0.2)
        )
        btn_advanced = Button(
            text='Erweiterte Einstellungen',
            size_hint=(1, 0.2)
        )
        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.2)
        )

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
        app = App.get_running_app()
        app.root.current = 'settings_patient'

    def zeige_alarm(self, instance):
        self._check_admin_pin_and_open('settings')

    def zeige_erweitert(self, instance):
        self._check_admin_pin_and_open('settings_advanced')

    def _check_admin_pin_and_open(self, target_screen_name):
        """Prüfen, ob Admin-PIN gesetzt ist und ggf. abfragen."""
        app = App.get_running_app()
        pin = getattr(app, 'admin_pin', '')

        if not pin:
            app.root.current = target_screen_name
            return

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text='Bitte Admin-PIN eingeben:',
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        pin_input = TextInput(
            multiline=False,
            password=True,
            size_hint=(1, 0.4)
        )

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.3)
        )
        btn_ok = Button(text='OK')
        btn_cancel = Button(text='Abbrechen')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(label)
        layout.add_widget(pin_input)
        layout.add_widget(btn_layout)

        popup = Popup(
            title='PIN-Schutz',
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )

        def on_ok(_inst):
            if pin_input.text == pin:
                popup.dismiss()
                app.root.current = target_screen_name
            else:
                label.text = 'Falscher PIN. Bitte erneut eingeben:'

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'