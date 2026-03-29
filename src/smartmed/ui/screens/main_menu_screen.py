from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Hauptmenü',
            font_size='28sp',
            size_hint=(1, 0.2)
        )

        btn_status = Button(text='Status anzeigen', size_hint=(1, 0.15))
        btn_plan = Button(text='Einnahmeplan', size_hint=(1, 0.15))
        btn_settings = Button(text='Einstellungen', size_hint=(1, 0.15))
        btn_log = Button(text='Log anzeigen', size_hint=(1, 0.15))
        btn_back = Button(text='zurück zum start', size_hint=(1, 0.15))

        btn_status.bind(on_press=self.zeige_status)
        btn_plan.bind(on_press=self.zeige_plan)
        btn_settings.bind(on_press=self.zeige_einstellungen)
        btn_log.bind(on_press=self.zeige_log)
        btn_back.bind(on_press=self.zurueck_zum_start)

        layout.add_widget(titel)
        layout.add_widget(btn_status)
        layout.add_widget(btn_plan)
        layout.add_widget(btn_settings)
        layout.add_widget(btn_log)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def zurueck_zum_start(self, instance):
        app = App.get_running_app()
        app.root.current = 'login'

    def zeige_status(self, instance):
        app = App.get_running_app()
        status_screen = app.root.get_screen('status')
        status_screen.tages_offset = 0
        status_screen.update_status()
        app.root.current = 'status'

    def zeige_plan(self, instance):
        app = App.get_running_app()
        plan_screen = app.root.get_screen('plan_list')
        plan_screen.update_liste()
        app.root.current = 'plan_list'

    def zeige_log(self, instance):
        app = App.get_running_app()
        log_screen = app.root.get_screen('log')
        log_screen.update_log()
        app.root.current = 'log'

    def zeige_einstellungen(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'
