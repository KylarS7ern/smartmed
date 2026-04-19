from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.services.event_log_service import get_log_entry_timestamp
from smartmed.ui.navigation import go_to_menu


class LogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Log',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        scroll = ScrollView(size_hint=(1, 0.75))

        self.log_label = Label(
            text='Noch keine Log-Einträge.',
            halign='left',
            valign='top',
            size_hint_y=None
        )

        self.log_label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', (val[0], None))
        )

        self.log_label.bind(
            texture_size=lambda inst, val: setattr(inst, 'height', val[1])
        )

        scroll.add_widget(self.log_label)

        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.1)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(scroll)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def update_log(self):
        """Log-Einträge aus der App holen und anzeigen."""
        app = App.get_running_app()
        log = getattr(app, 'log_eintraege', [])

        if not log:
            self.log_label.text = 'Noch keine Log-Einträge.'
            return

        eintraege = list(log)
        eintraege.reverse()

        lines = []
        for entry in eintraege:
            ts = get_log_entry_timestamp(entry)
            txt = entry.get('text', '')
            lines.append(f"{ts} - {txt}")

        self.log_label.text = '\n'.join(lines)

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)