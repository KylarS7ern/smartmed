from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from smartmed.ui.navigation import go_to_menu

from smartmed.services.user_account_service import (
    create_user_result,
    list_sorted_usernames,
    user_requires_password,
    verify_user_password,
)


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

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            spacing=10
        )

        btn_new = Button(text='Neuen Benutzer anlegen')
        btn_exit = Button(text='App beenden')

        btn_new.bind(on_press=self.neuen_benutzer)
        btn_exit.bind(on_press=self.app_beenden_bestaetigen)

        btn_row.add_widget(btn_new)
        btn_row.add_widget(btn_exit)

        root.add_widget(titel)
        root.add_widget(scroll)
        root.add_widget(btn_row)

        self.add_widget(root)

    def app_beenden_bestaetigen(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text='App wirklich beenden?',
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.35)
        )

        btn_yes = Button(text='Ja')
        btn_no = Button(text='Nein')

        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = Popup(
            title='Beenden',
            content=layout,
            size_hint=(0.7, 0.35),
            auto_dismiss=False
        )

        btn_yes.bind(on_press=lambda *_: App.get_running_app().stop())
        btn_no.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def on_pre_enter(self, *args):
        """Aktuelle Benutzerliste anzeigen, wenn Screen gezeigt wird."""
        app = App.get_running_app()

        self.user_list_layout.clear_widgets()

        for username in list_sorted_usernames(app.users):
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

        if not user_requires_password(app.users, username):
            app.switch_user(username)
            go_to_menu(app)
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
            result = verify_user_password(
                app.users,
                username,
                pw_input.text,
            )

            if result['ok']:
                popup.dismiss()
                app.switch_user(username)
                go_to_menu(app)
            else:
                label.text = result['message']

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
            result = create_user_result(
                users=app.users,
                username_text=name_input.text,
                password_text=pw_input.text,
                settings=app.settings,
            )

            if not result['ok']:
                lbl_name.text = result['message']
                return

            app.users[result['username']] = result['user_data']

            popup.dismiss()
            app.switch_user(result['username'])
            go_to_menu(app)

        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())

        popup.open()
