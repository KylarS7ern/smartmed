from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from smartmed.ui import theme
from smartmed.ui.navigation import (
    go_to_log,
    go_to_login,
    go_to_plan_list,
    go_to_settings_menu,
    go_to_status,
)
from smartmed.ui.widgets import PrimaryButton, SecondaryButton, TitleLabel


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Hauptmenü',
            size_hint=(1, 0.18)
        )

        btn_kwargs = dict(font_size=theme.FONT_XLARGE, size_hint=(1, 0.15))

        btn_status = PrimaryButton(text='Status anzeigen', **btn_kwargs)
        btn_plan = PrimaryButton(text='Einnahmeplan', **btn_kwargs)
        btn_settings = PrimaryButton(text='Einstellungen', **btn_kwargs)
        btn_log = PrimaryButton(text='Log anzeigen', **btn_kwargs)
        btn_back = SecondaryButton(text='Benutzer wechseln', **btn_kwargs)

        btn_status.bind(on_press=self.zeige_status)
        btn_plan.bind(on_press=self.zeige_plan)
        btn_settings.bind(on_press=self.zeige_einstellungen)
        btn_log.bind(on_press=self.zeige_log)
        btn_back.bind(on_press=self.benutzer_wechseln)

        layout.add_widget(titel)
        layout.add_widget(btn_status)
        layout.add_widget(btn_plan)
        layout.add_widget(btn_settings)
        layout.add_widget(btn_log)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def benutzer_wechseln(self, instance):
        app = App.get_running_app()
        go_to_login(app)

    def zeige_status(self, instance):
        app = App.get_running_app()
        go_to_status(app)

    def zeige_plan(self, instance):
        app = App.get_running_app()
        go_to_plan_list(app)

    def zeige_log(self, instance):
        app = App.get_running_app()
        go_to_log(app)

    def zeige_einstellungen(self, instance):
        app = App.get_running_app()
        go_to_settings_menu(app)
