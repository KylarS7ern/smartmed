from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        titel = Label(
            text='SmartMedSpender',
            font_size='32sp',
            size_hint=(1, 0.2)
        )

        button = Button(
            text='Zum Hauptmenü',
            font_size='24sp',
            size_hint=(1, 0.2)
        )

        button.bind(on_press=self.wechsle_zu_menue)

        layout.add_widget(titel)
        layout.add_widget(button)

        self.add_widget(layout)

    def wechsle_zu_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'
