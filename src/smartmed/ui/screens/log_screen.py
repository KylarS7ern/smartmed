from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.services.event_log_service import get_log_entry_timestamp
from smartmed.ui import theme
from smartmed.ui.navigation import go_to_menu
from smartmed.ui.widgets import MutedLabel, PrimaryButton, SecondaryButton, TitleLabel


class LogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Log',
            size_hint=(1, None),
            height=dp(48)
        )

        scroll = ScrollView(size_hint=(1, 1))

        self.log_label = Label(
            text='Noch keine Log-Einträge.',
            font_size=theme.FONT_BODY,
            color=theme.TEXT_PRIMARY,
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

        self.status_label = MutedLabel(
            text='',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(36)
        )
        self.status_label.bind(
            width=lambda inst, val: setattr(inst, 'text_size', (val, None))
        )
        self.status_label.bind(
            texture_size=lambda inst, val: setattr(inst, 'height', max(dp(36), val[1]))
        )

        btn_export = PrimaryButton(
            text='Log als Datei exportieren (.txt)',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_export.bind(on_press=self.exportieren)

        btn_email = PrimaryButton(
            text='Log per E-Mail senden',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_email.bind(on_press=self.per_email_senden)

        btn_back = SecondaryButton(
            text='Zurück zum Hauptmenü',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(scroll)
        layout.add_widget(self.status_label)
        layout.add_widget(btn_export)
        layout.add_widget(btn_email)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.status_label.text = ''
        self.update_log()

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

    def exportieren(self, instance):
        app = App.get_running_app()
        result = app.exportiere_log()
        self.status_label.text = result.get('message', '')
        self.update_log()

    def per_email_senden(self, instance):
        app = App.get_running_app()
        result = app.sende_log_per_email()
        self.status_label.text = result.get('message', '')
        self.update_log()

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)
