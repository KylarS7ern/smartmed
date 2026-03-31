from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from smartmed.models.defaults import build_default_user


class UserLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Benutzer auswählen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        scroll = ScrollView(size_hint=(1, 0.6))
        self.user_list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )
        self.user_list_layout.bind(
            minimum_height=self.user_list_layout.setter('height')
        )
        scroll.add_widget(self.user_list_layout)

        btn_new = Button(
            text='Neuen Benutzer anlegen',
            size_hint=(1, 0.15)
        )
        btn_new.bind(on_press=self.neuen_benutzer)

        root.add_widget(titel)
        root.add_widget(scroll)
        root.add_widget(btn_new)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        """Aktuelle Benutzerliste anzeigen, wenn Screen gezeigt wird."""
        app = App.get_running_app()

        self.user_list_layout.clear_widgets()

        for username in sorted(app.users.keys()):
            btn = Button(
                text=username,
                size_hint_y=None,
                height=50
            )
            btn.bind(on_press=lambda inst, name=username: self.login_benutzer(name))
            self.user_list_layout.add_widget(btn)

    def login_benutzer(self, username):
        """Passwort abfragen (falls gesetzt) und Benutzer einloggen."""
        app = App.get_running_app()

        user = app.users.get(username, {})
        gespeichertes_pw = user.get('password', '')

        if not gespeichertes_pw:
            app.switch_user(username)
            self.manager.current = 'menu'
            return

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=f'Passwort für "{username}" eingeben:',
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        pw_input = TextInput(
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
        layout.add_widget(pw_input)
        layout.add_widget(btn_layout)

        popup = Popup(
            title='Anmeldung',
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )

        def on_ok(_inst):
            if pw_input.text == gespeichertes_pw:
                popup.dismiss()
                app.switch_user(username)
                app.root.current = 'menu'
            else:
                label.text = 'Falsches Passwort. Bitte erneut eingeben:'

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def neuen_benutzer(self, instance):
        """Popup zum Anlegen eines neuen Benutzers."""
        app = App.get_running_app()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        lbl_name = Label(
            text='Benutzername:',
            halign='left',
            valign='middle'
        )
        lbl_name.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        name_input = TextInput(multiline=False)

        lbl_pw = Label(
            text='Passwort (optional):',
            halign='left',
            valign='middle'
        )
        lbl_pw.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        pw_input = TextInput(multiline=False, password=True)

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.3)
        )
        btn_ok = Button(text='Anlegen')
        btn_cancel = Button(text='Abbrechen')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(lbl_name)
        layout.add_widget(name_input)
        layout.add_widget(lbl_pw)
        layout.add_widget(pw_input)
        layout.add_widget(btn_layout)

        popup = Popup(
            title='Neuen Benutzer',
            content=layout,
            size_hint=(0.85, 0.6),
            auto_dismiss=False
        )

        def on_ok(_inst):
            username = name_input.text.strip()
            password = pw_input.text.strip()

            if not username:
                lbl_name.text = 'Benutzername darf nicht leer sein. Bitte eingeben:'
                return

            if username in app.users:
                lbl_name.text = 'Benutzername existiert bereits. Bitte anderen Namen wählen:'
                return

            app.users[username] = build_default_user(
                username=username,
                password=password,
                patient_name=username,
                patient_geburt='-',
                settings=app.settings,
            )

            popup.dismiss()
            app.switch_user(username)
            app.root.current = 'menu'

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())

        popup.open()
