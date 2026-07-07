from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.ui import theme
from smartmed.ui.navigation import go_to_menu
from smartmed.ui.widgets import (
    BodyLabel,
    DangerButton,
    PrimaryButton,
    SecondaryButton,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    make_popup,
)

from smartmed.services.user_account_service import (
    create_user_result,
    list_sorted_usernames,
    user_requires_password,
    verify_user_password,
)
from smartmed.services.security_service import hash_secret


class UserLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Benutzer auswählen',
            size_hint=(1, 0.15)
        )

        scroll = ScrollView(size_hint=(1, 0.6))
        self.user_list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=theme.SPACING
        )
        self.user_list_layout.bind(
            minimum_height=self.user_list_layout.setter('height')
        )
        scroll.add_widget(self.user_list_layout)

        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            spacing=theme.SPACING
        )

        btn_new = PrimaryButton(text='Neuen Benutzer anlegen')
        btn_exit = SecondaryButton(text='App beenden')

        btn_new.bind(on_press=self.neuen_benutzer)
        btn_exit.bind(on_press=self.app_beenden_bestaetigen)

        btn_row.add_widget(btn_new)
        btn_row.add_widget(btn_exit)

        root.add_widget(titel)
        root.add_widget(scroll)
        root.add_widget(btn_row)

        self.add_widget(root)

    def app_beenden_bestaetigen(self, instance):
        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text='App wirklich beenden?',
            halign='center',
            valign='middle'
        )

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, 0.35)
        )

        btn_yes = DangerButton(text='Ja')
        btn_no = SecondaryButton(text='Nein')

        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Beenden', content=layout, size_hint=(0.7, 0.35))

        btn_yes.bind(on_press=lambda *_: App.get_running_app().stop())
        btn_no.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def on_pre_enter(self, *args):
        """Aktuelle Benutzerliste anzeigen, wenn Screen gezeigt wird."""
        app = App.get_running_app()

        self.user_list_layout.clear_widgets()

        for username in list_sorted_usernames(app.users):
            btn = PrimaryButton(
                text=username,
                font_size=theme.FONT_XLARGE,
                size_hint_y=None,
                height=dp(72)
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

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=f'Passwort für "{username}" eingeben:',
            halign='center',
            valign='middle'
        )

        pw_input = StyledTextInput(
            multiline=False,
            password=True,
            size_hint=(1, 0.4)
        )

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, 0.3)
        )
        btn_ok = SuccessButton(text='OK')
        btn_cancel = SecondaryButton(text='Abbrechen')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(label)
        layout.add_widget(pw_input)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Anmeldung', content=layout, size_hint=(0.8, 0.5))

        def on_ok(_inst):
            result = verify_user_password(
                app.users,
                username,
                pw_input.text,
            )

            if result['ok']:
                if result.get('needs_rehash'):
                    app.users[username]['password'] = hash_secret(pw_input.text)
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

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        lbl_name = BodyLabel(
            text='Benutzername:',
            halign='left',
            valign='middle'
        )
        name_input = StyledTextInput(multiline=False)

        lbl_pw = BodyLabel(
            text='Passwort (optional):',
            halign='left',
            valign='middle'
        )
        pw_input = StyledTextInput(multiline=False, password=True)

        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, 0.3)
        )
        btn_ok = SuccessButton(text='Anlegen')
        btn_cancel = SecondaryButton(text='Abbrechen')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)

        layout.add_widget(lbl_name)
        layout.add_widget(name_input)
        layout.add_widget(lbl_pw)
        layout.add_widget(pw_input)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Neuen Benutzer', content=layout, size_hint=(0.85, 0.6))

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
