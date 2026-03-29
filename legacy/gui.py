from smartmed.config import DATA_FILE
from smartmed.services.storage_service import load_json_data, save_json_data
from smartmed.models.defaults import build_default_settings, build_default_user
from smartmed.services.notification_service import send_alarm_notifications


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN =  ''

EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587
EMAIL_USERNAME = 'smartmedispender@gmail.com'
EMAIL_PASSWORT = ''


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

    def wechsle_zu_menue(self, instamce):

        app = App.get_running_app()
        app.root.current ='menu'

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
        btn_back.bind(on_press=self.zurück_zum_start)

        layout.add_widget(titel)
        layout.add_widget(btn_status)
        layout.add_widget(btn_plan)
        layout.add_widget(btn_settings)
        layout.add_widget(btn_log)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def zurück_zum_start(self, instance):
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

class PlanEintragErfassenScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bearbeite_eintrag = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Neue Einnahme-Eintrag anlegen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        self.med_input = TextInput(
            hint_text='Medikamentenname',
            multiline=False,
            size_hint=(1, 0.15)
        )

        self.fach_spinner = Spinner(
            text='Fach wählen',
            values=('1', '2', '3', '4', '5', '6'),
            size_hint=(1, 0.15)
        )

        self.tag_spinner = Spinner(
            text='Wochentag wählen',
            values=('Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'),
            size_hint=(1, 0.15)
        )

        self.anzahl_spinner = Spinner(
            text='Anzahl Pillen',
            values=('1', '2', '3', '4', '5'),
            size_hint=(1, 0.15)
        )

        self.fach_info_label = Label(
            text='Fach: (noch nichts gewählt)',
            font_size='14sp',
            size_hint=(1, 0.1)
        )

        self.fach_spinner.bind(text=self.on_fach_gewaehlt)

        stunden = [f'{h:02d}' for h in range (0, 24)]
        minuten = [f'{m:02d}' for m in range (0, 60, 5)]

        uhrzeit_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))

        self.stunde_spinner = Spinner(
            text='Stunde',
            values=tuple(stunden),
            size_hint=(0.5, 1)
        )

        self.minute_spinner = Spinner(
            text='Minute',
            values=tuple(minuten),
            size_hint=(0.5, 1)
        )

        uhrzeit_layout.add_widget(self.stunde_spinner)
        uhrzeit_layout.add_widget(self.minute_spinner)

        btn_speichern = Button(
            text='Eintrag speichern',
            size_hint=(1, 0.15)
        )
        btn_speichern.bind(on_press=self.speichern_eintrag)

        btn_back  = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.15)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(self.med_input)
        layout.add_widget(self.fach_spinner)
        layout.add_widget(self.fach_info_label)
        layout.add_widget(self.tag_spinner)
        layout.add_widget(self.anzahl_spinner)
        layout.add_widget(uhrzeit_layout)
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def zeige_meldung(self, text):
        """zeigt eine einfache Hinweis-Popup-Meldung an."""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=text,
            halign='center',
            valign='middle'
        )

        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_ok = Button(
            text='OK',
            size_hint=(1, 0.3)
        )

        popup = Popup(
            title='Hinweis',
            content=layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        btn_ok.bind(on_press=popup.dismiss)

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup.open()

    def on_fach_gewaehlt(self, spinner, value):
        """Wird aufgerufen, wenn im Fach-Spinner ein Fach gewählt wird."""
        app = App.get_running_app()

        med = app.fach_medikamente.get(value)

        if med:

            self.fach_info_label.text = f"Fach {value}: {med}"

            if not self.med_input.text.strip():
                self.med_input.text = med
        else:
            self.fach_info_label.text = f"Fach {value}: noch leer"

    def speichern_eintrag(self, instance):
        """Einen neuen Eintrag speichern ode rbestehenden Eintrag aktualisieren."""
        app = App.get_running_app()

        med = self.med_input.text.strip()
        fach = self.fach_spinner.text.strip()
        tag = self.tag_spinner.text.strip()
        stunde = self.stunde_spinner.text.strip()
        minute = self.minute_spinner.text.strip()
        anzahl = self.anzahl_spinner.text.strip()

        if (
            not med or 
            fach.startswith('Fach') or
            tag.startswith('Wochentag') or 
            anzahl.startswith('Anzahl') or 
            stunde == 'Stunde' or 
            minute == 'Minute'
        ):
            print('Bitte alle Felder auswählen/ausfüllen.')
            return
        
        zeit = f'{stunde}:{minute}'
        anzahl_int = int(anzahl)

        if self.bearbeite_eintrag is not None:

            vorhandenes_med = app.fach_medikamente.get(fach)
            if vorhandenes_med and vorhandenes_med != med and fach != self.bearbeite_eintrag.get('fach'):
                self.zeige_meldung(
                    f"Fach {fach} ist bereits mit '{vorhandenes_med}' belegt.\n"
                    'Bitte zuerst dort den Eintrag ändern oder löschen.'
                )
                return

            altes_fach = self.bearbeite_eintrag.get('fach')
            altes_med = self.bearbeite_eintrag.get('medikament')
            
            self.bearbeite_eintrag['medikament'] = med
            self.bearbeite_eintrag['fach'] = fach
            self.bearbeite_eintrag['tag'] = tag
            self.bearbeite_eintrag['zeit'] = zeit
            self.bearbeite_eintrag['anzahl'] = int(anzahl)

            print('Eintrag aktualisiert:', self.bearbeite_eintrag)

            app.fach_medikamente = {}
            for e in app.plan_eintraege:
                f = e.get('fach')
                m = e.get('medikament')
                if f and f not in app.fach_medikamente:
                    app.fach_medikamente[f] = m

            app.log_event(
                f"Plan-Eintrag geändert: {tag} {zeit} | Fach {fach} | {med} (x{anzahl_int})"
            )
    
            app.save_data()
            self.felder_zuruecksetzen()
            return

        vorhandenes_med = app.fach_medikamente.get(fach)

        if vorhandenes_med is None:
            app.fach_medikamente[fach] = med
            print(f'Fach {fach} jetzt belegt mit: {med}')
        elif vorhandenes_med != med:
            meldung = (
                f"Fach {fach} ist bereits mit '{vorhandenes_med}' belegt.\n\n"
                "Bitte zuerst die Einträge / Belegung ändern, bevor ein anderes "
                "Medikament für dieses Fach verwendet wird."
            )

            self.zeige_meldung(meldung)
            self.med_input.text = vorhandenes_med
            return
        
        eintrag ={
            'medikament': med,
            'fach': fach,
            'tag': tag,
            'zeit':zeit,
            'anzahl': anzahl_int
        }

        app.plan_eintraege.append(eintrag)
        print('Neuer eintrag gespeichert:', eintrag)

        app.log_event(
            f"Plan-Eintrag neu: {tag} {zeit} | Fach {fach} | {med} (x{anzahl_int})"
        )

        app.save_data()
        self.felder_zuruecksetzen()

    def felder_zuruecksetzen(self):
        """Eingabefelder wieder in Grundzustand setzen."""
        self.bearbeite_eintrag = None
        self.med_input.text = ''
        self.fach_spinner.text = 'Fach wählen'
        self.fach_info_label.text ='Fach: (noch nichts gewählt)'
        self.tag_spinner.text = 'Wochentag wählen'
        self.anzahl_spinner.text = 'Anzahl Pillen'
        self.stunde_spinner.text = 'Stunde'
        self.minute_spinner.text = 'Minute'

    def start_bearbeiten(self, eintrag):
        """Bestehenden Eintrag in die Felder laden und Bearbeitungsmodus aktivieren."""
        self.bearbeite_eintrag = eintrag

        med = eintrag.get('medikament', '')
        fach = eintrag.get('fach', '')
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')
        anzahl = eintrag.get('anzahl', 1)

        try:
            stunde, minute = zeit.split(':')
        except ValueError:
            stunde, minute = '00', '00'

        self.med_input.text = med
        self.fach_spinner.text = fach
        self.tag_spinner.text = tag
        self.anzahl_spinner.text = str(anzahl)
        self.stunde_spinner.text = stunde
        self.minute_spinner.text = minute

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'        

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
            size=lambda inst, val:setattr(inst, 'text_size', (val[0], None))
        )

        self.log_label.bind(
            texture_size=lambda inst, val:setattr(inst, 'height', val[1])
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
            ts = entry.get('zeit', '')
            txt = entry.get('text', '')
            lines.append(f"{ts} - {txt}")

        self.log_label.text = '\n'.join(lines)

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )

        titel = Label(
            text='Alarm-Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        btn_info = Button(
            text='!',
            size_hint=(0.2, 1)
        )
        btn_info.bind(on_press=self.zeige_info_popup)

        titel_layout.add_widget(titel)
        titel_layout.add_widget(btn_info)

        alarm_delay_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_delay = Label(
            text='Zeit bis Alarm (Minuten):',
            size_hint=(0.6, 1)
        )
        self.alarm_delay_input = TextInput(
            multiline=False,
            input_filter='int',
            size_hint=(0.4, 1)
        )
        alarm_delay_layout.add_widget(lbl_delay)
        alarm_delay_layout.add_widget(self.alarm_delay_input)

        alarm_mode_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_mode = Label(
            text='Art des Alarms:',
            size_hint=(0.6, 1)
        )
        self.alarm_mode_spinner = Spinner(
            text='Popup + Log',
            values=('Popup + Log', 'Nur Log'),
            size_hint=(0.4, 1)
        )
        alarm_mode_layout.add_widget(lbl_mode)
        alarm_mode_layout.add_widget(self.alarm_mode_spinner)

        notify_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_notify = Label(
            text='Benachrichtigung:',
            size_hint=(0.6, 1)
        )
        self.notify_spinner = Spinner(
            text='Nichts',
            values=('Nichts', 'Nur E-Mail', 'Nur Telegram', 'E-Mail + Telegram'),
            size_hint=(0.4, 1)
        )
        notify_layout.add_widget(lbl_notify)
        notify_layout.add_widget(self.notify_spinner)

        email_choice_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_email_choice = Label(
            text='Empfänger wählen:',
            size_hint=(0.6, 1)
        )
        self.email_recipients_spinner = Spinner(
            text='Manuell',
            values=('Manuell', 'Arzt', 'Kontakt 1', 'Kontakt 2'),
            size_hint=(0.4, 1)
        )
        self.email_recipients_spinner.bind(text=self.on_email_recipient_changed)

        email_choice_layout.add_widget(lbl_email_choice)
        email_choice_layout.add_widget(self.email_recipients_spinner)

        email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_email = Label(
            text='E-Mail Empfänger:',
            size_hint=(0.6, 1)
        )
        self.email_to_input = TextInput(
            multiline=False,
            size_hint=(0.4, 1)
        )
        email_layout.add_widget(lbl_email)
        email_layout.add_widget(self.email_to_input)

        telegram_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.15)
        )
        lbl_tg = Label(
            text='Telegram Chat-ID:',
            size_hint=(0.6, 1)
        )
        self.telegram_chat_id_input = TextInput(
            multiline=False,
            size_hint=(0.4, 1)
        )
        telegram_layout.add_widget(lbl_tg)
        telegram_layout.add_widget(self.telegram_chat_id_input)

        btn_test = Button(
            text='Testnachricht senden',
            size_hint=(1, 0.15)
        )
        btn_test.bind(on_press=self.sende_testnachricht)


        btn_speichern = Button(
            text='Einstellungen speichern',
            size_hint=(1, 0.15)
        )
        btn_speichern.bind(on_press=self.speichern_einstellungen)

        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.15)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel_layout)
        layout.add_widget(alarm_delay_layout)
        layout.add_widget(alarm_mode_layout)
        layout.add_widget(notify_layout)
        layout.add_widget(email_choice_layout)
        layout.add_widget(email_layout)
        layout.add_widget(telegram_layout)
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_test)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        """Aktuelle Einstellungen ins UI laden, wenn Screeen angezeigt wird."""

        app = App.get_running_app()

        delay = app.settings.get('alarm_delay_min', 30)
        self.alarm_delay_input.text = str(delay)

        mode = app.settings.get('alarm_mode', 'popup')
        if mode == 'log':
            self.alarm_mode_spinner.text = 'Nur Log'
        else: 
            self.alarm_mode_spinner.text = 'Popup + Log' 

        notify_mode = app.settings.get('notify_mode', 'none')
        if notify_mode == 'email':
            self.notify_spinner.text = 'Nur E-Mail'
        elif notify_mode == 'telegram':
            self.notify_spinner.text = 'Nur Telegram'
        elif notify_mode == 'both':
            self.notify_spinner.text = 'E-Mail + Telegram'
        else:
            self.notify_spinner.text = 'Nichts'

        email_recipient = app.settings.get('email_recipient', 'manual')
        if email_recipient == 'doctor':
            self.email_recipients_spinner.text = 'Arzt'
        elif email_recipient == 'contact1':
            self.email_recipients_spinner.text = 'Kontakt 1'
        elif email_recipient == 'contact2':
            self.email_recipients_spinner.text = 'Kontakt 2'
        else:
            self.email_recipients_spinner.text = 'Manuell'

        self.email_to_input.text = app.settings.get('email_to', '')
        self.telegram_chat_id_input.text = app.settings.get('telegram_chat_id', '')

    def zeige_info_popup(self, instance):
        """Zeigt die ausführliche Anleitung zur Benachrichtigung als Popup an."""
        info_text = (
            'Benachrichtigungen einrichten:\n\n'
            '1) E-Mail:\n'
            "   - Unten im Feld \"E-Mail Empfänger\" die Adresse der\n"
            "     Kontaktperson eintragen (z.B. mutter@example.com).\n"
            "   - Auf dem Handy der Kontaktperson muss eine Mail-App\n"
            "     eingerichtet sein, damit eine Push-Nachricht erscheint.\n\n"
            "2) Telegram:\n"
            "   - Auf dem Handy die Telegram-App öffnen.\n"
            "   - Den SmartMedSpender-Bot suchen (z.B. @SmartMedSpenderBot)\n"
            "     und auf \"Start\" tippen.\n"
            "   - Die Telegram-Chat-ID wird normalerweise vom Betreuer/\n"
            "     Techniker ermittelt und hier im Feld \"Telegram Chat-ID\"\n"
            "     eingetragen.\n\n"
            "3) Oben unter \"Benachrichtigung\" auswählen, ob nichts,\n"
            "   nur E-Mail, nur Telegram oder beides verwendet werden soll.\n\n"
            "4) Mit \"Testnachricht senden\" können Sie prüfen,\n"
            '   ob alles klappt.'
        )

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=info_text,
            halign='left',
            valign='top'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_ok = Button(
            text='Schliessen',
            size_hint=(1, 0.2)
        )

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup = Popup(
            title='Hilfe zu Benachrichtigungen',
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )

        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def on_email_recipient_changed(self, spinner, value):
        """Wenn Empfänger-Auswahl geändert wird, passende Adresse einsetzen."""
        app = App.get_running_app()
        
        if value == 'Arzt':
            email = getattr(app, 'doctor_email', '').strip()
            self.email_to_input.text = email
        elif value == 'Kontakt 1':
            email = getattr(app, 'contact1_email', '').strip()
            self.email_to_input.text = email
        elif value == 'Kontakt 2':
            email = getattr(app, 'contact2_email', '').strip()
            self.email_to_input.text = email
        else:
            pass

    def sende_testnachricht(self, instance):
        app = App.get_running_app()

        self.speichern_einstellungen(instance)

        dummy_eintrag = {
            'tag': 'Mo',
            'zeit': '12:00',
            'fach': '1',
            'medikament': 'Test-Medikament',
            'anzahl': 1,
        }
        app.sende_alarm_benachrichtigungen(dummy_eintrag)

    def speichern_einstellungen(self, instance):
        app = App.get_running_app()

        try:
            delay = int(self.alarm_delay_input.text.strip() or '30')
            if delay <= 0:
                raise ValueError()
        except ValueError:
            delay = 30
            print("Ungültige Alarmeit, auf 30 minten gesetzt.")

        app.settings['alarm_delay_min'] = delay

        text = self.alarm_mode_spinner.text
        if text == 'Nur Log':
            mode = 'log'
        else:
            mode = 'popup' 
        app.settings['alarm_mode'] = mode

        nt = self.notify_spinner.text
        if nt == 'Nur E-Mail':
            notify_mode = 'email'
        elif nt == 'Nur Telegram':
            notify_mode = 'telegram'
        elif nt == 'E-Mail + Telegram':
            notify_mode = 'both'
        else:
            notify_mode = 'none'
        app.settings['notify_mode'] = notify_mode

        app.settings['email_to'] = self.email_to_input.text.strip()
        app.settings['telegram_chat_id'] = self.telegram_chat_id_input.text.strip()

        er_text = self.email_recipients_spinner.text
        if er_text == 'Arzt':
            app.settings['email_recipient'] = 'doctor'
        elif er_text == 'Kontakt 1':
            app.settings['email_recipient'] = 'contact1'
        elif er_text == 'Kontakt 2':
            app.settings['email_recipient'] = 'contact2'
        else:
            app.settings['email_recipient'] = 'manual'

        app.save_data()
        print('Alarm-Einstellungen gespeichert:', app.settings)

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'

class PatientSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Patienten-Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_name = Label(
            text='Name:',
            size_hint=(0.4, 1)
        )
        self.name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        name_layout.add_widget(lbl_name)
        name_layout.add_widget(self.name_input)

        geburt_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_geburt = Label(
            text='Geburtsdatum:',
            size_hint=(0.4, 1)
        )
        self.geburt_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        geburt_layout.add_widget(lbl_geburt)
        geburt_layout.add_widget(self.geburt_input)

        lbl_address = Label(
            text='Adresse:',
            size_hint=(1, 0.1)
        )
        self.address_input = TextInput(
            multiline=True,
            size_hint=(1, 0.25)
        )

        doc_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_name = Label(
            text='Arzt (Name):',
            size_hint=(0.4, 1)
        )
        self.doc_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_name_layout.add_widget(lbl_doc_name)
        doc_name_layout.add_widget(self.doc_name_input)

        doc_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_email = Label(
            text='Arzt E-Mail:',
            size_hint=(0.4, 1)
        )
        self.doc_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_email_layout.add_widget(lbl_doc_email)
        doc_email_layout.add_widget(self.doc_email_input)

        doc_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_phone = Label(
            text='Arzt Telefon:',
            size_hint=(0.4, 1)
        )
        self.doc_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_phone_layout.add_widget(lbl_doc_phone)
        doc_phone_layout.add_widget(self.doc_phone_input)

        c1_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_name = Label(
            text='Kontakt 1 Name:',
            size_hint=(0.4, 1)
        )
        self.c1_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_name_layout.add_widget(lbl_c1_name)
        c1_name_layout.add_widget(self.c1_name_input)

        c1_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_email = Label(
            text='Kontakt 1 E-Mail:',
            size_hint=(0.4, 1)
        )
        self.c1_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_email_layout.add_widget(lbl_c1_email)
        c1_email_layout.add_widget(self.c1_email_input)

        c1_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_phone = Label(
            text='Kontakt 1 Telefon:',
            size_hint=(0.4, 1)
        )
        self.c1_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_phone_layout.add_widget(lbl_c1_phone)
        c1_phone_layout.add_widget(self.c1_phone_input)

        c2_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_name = Label(
            text='Kontakt 2 Name:',
            size_hint=(0.4, 1)
        )
        self.c2_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_name_layout.add_widget(lbl_c2_name)
        c2_name_layout.add_widget(self.c2_name_input)

        c2_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_email = Label(
            text='Kontakt 2 E-Mail:',
            size_hint=(0.4, 1)
        )
        self.c2_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_email_layout.add_widget(lbl_c2_email)
        c2_email_layout.add_widget(self.c2_email_input)

        c2_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_phone = Label(
            text='Kontakt 2 Telefon:',
            size_hint=(0.4, 1)
        )
        self.c2_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_phone_layout.add_widget(lbl_c2_phone)
        c2_phone_layout.add_widget(self.c2_phone_input)

        btn_speichern = Button(
            text='Patientendaten speichern',
            size_hint=(1, 0.12)
        )
        btn_speichern.bind(on_press=self.speichern_patient)

        btn_back = Button(
            text='Zurück',
            size_hint=(1, 0.2)
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(titel)
        layout.add_widget(name_layout)
        layout.add_widget(geburt_layout)
        layout.add_widget(lbl_address)
        layout.add_widget(self.address_input)
        layout.add_widget(doc_name_layout)
        layout.add_widget(doc_email_layout)
        layout.add_widget(doc_phone_layout)
        layout.add_widget(c1_name_layout)
        layout.add_widget(c1_email_layout)
        layout.add_widget(c1_phone_layout)
        layout.add_widget(c2_name_layout)
        layout.add_widget(c2_email_layout)
        layout.add_widget(c2_phone_layout)
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        """Beim Öffnen aktuelle Daten laden."""
        app = App.get_running_app()
        self.name_input.text = str(getattr(app, 'patient_name', '') or '')
        self.geburt_input.text = str(getattr(app, 'patient_geburt', '') or '')
        self.address_input.text = str(getattr(app, 'patient_address', '') or '')
        self.doc_name_input.text = str(getattr(app, 'doctor_name', '') or '')
        self.doc_email_input.text = str(getattr(app, 'doctor_email', '') or '')
        self.doc_phone_input.text = str(getattr(app, 'doctor_phone', '') or '')
        self.c1_name_input.text = str(getattr(app, 'contact1_name', '') or '')
        self.c1_email_input.text = str(getattr(app, 'contact1_email', '') or '')
        self.c1_phone_input.text = str(getattr(app, 'contact1_phone', '') or '')
        self.c2_name_input.text = str(getattr(app, 'contact2_name', '') or '')
        self.c2_email_input.text = str(getattr(app, 'contact2_email', '') or '')
        self.c2_phone_input.text = str(getattr(app, 'contact2_phone', '') or '')

    def speichern_patient(self, instance):
        app = App.get_running_app()
        app.patient_name = self.name_input.text.strip() or 'Demo-Patient'
        app.patient_geburt = self.geburt_input.text.strip() or '-'
        app.patient_address = self.address_input.text.strip() 
        app.doctor_name = self.doc_name_input.text.strip() 
        app.doctor_email = self.doc_email_input.text.strip()
        app.doctor_phone = self.doc_phone_input.text.strip()
        app.contact1_name = self.c1_name_input.text.strip()
        app.contact1_email = self.c1_email_input.text.strip()
        app.contact1_phone = self.c1_phone_input.text.strip()
        app.contact2_name = self.c2_name_input.text.strip()
        app.contact2_email = self.c2_email_input.text.strip()
        app.contact2_phone = self.c2_phone_input.text.strip() 


        app.save_data()
        print('Patientendaten gespeichert:', app.patient_name, app.patient_geburt)

    def zurueck(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'

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
            'z.B. WLAN, Zeitsynchronisation, Backup/Restore, Fach-Medikament, Passwortscshutz ect.'
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
        if getattr(app, 'admin_pin', ''):
            self.pin_info_label.text = 'Aktueller Status: PIN ist gesetzt'
        else:
            self.pin_info_label.text = 'Aktueller Status: Kein PIN gesetzt'
        self.pin_input.text = ''
        self.pin_repeat_input.text = ''

    def speichern_pin(self, instance):
        """Admin-PIN speichern oder entfernen."""
        app = App.get_running_app()
        pin1 = self.pin_input.text.strip()
        pin2 = self.pin_repeat_input.text.strip()

        if not pin1 and not pin2:
            app.admin_pin = ''
            app.save_data()
            self.pin_info_label.text = 'PIN-Schutz wurde deaktiviert.'
            return
        
        if pin1 != pin2:
            self.pin_info_label.text = 'Die eingegebenen PINs stimmen nicht überein.'
            return
        
        if len(pin1) < 4:
            self.pin_info_label.text = 'PIN muss mindestens 4 Zeichen lang sein.'
            return  
        
        app.admin_pin = pin1
        app.save_data()
        self.pin_info_label.text = 'Admin-PIN wurde gespeichert.'
            
    def zurueck(self, instance):
        app = App.get_running_app()
        app.root.current = 'settings_menu'

class StatusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tages_offset  = 0

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Status',
            font_size='21sp',
            size_hint=(1, 0.12)
        )

        self.datetime_label = Label(
            text='',
            font_size='14sp',
            size_hint=(1, 0.1)
        )

        nav_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )

        btn_prev = Button(
            text='< Tag zurück',
            size_hint=(0.5, 1)
        )
        btn_prev.bind(on_press=self.tag_zurueck)

        btn_next = Button(
            text='Tag vor >',
            size_hint=(0.5, 1)
        )
        btn_next.bind(on_press=self.tag_vor)

        nav_layout.add_widget(btn_prev)
        nav_layout.add_widget(btn_next)
    

        self.status_label = Label(
            text='Lade Status...',
            halign='center',
            valign='middle',
            size_hint=(1, 0.6)
        )

        self.status_label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', val)
            )

        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.1)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(self.datetime_label)
        layout.add_widget(nav_layout)
        layout.add_widget(self.status_label)
        layout.add_widget(btn_back)

        self.add_widget(layout)

        Clock.schedule_interval(self.update_datetime, 1.0)

    def update_datetime(self, *args):
        """Datum/Uhrzeit-Label aktualisieren."""
        jetzt = datetime.now()
        self.datetime_label.text = jetzt.strftime('%d.%m.%Y  %H:%M:%S')

    def update_status(self):
        """Status-text aus dem App-Zustand aktualisieren."""
        app = App.get_running_app()
        name = getattr(app, 'patient_name', 'Unbekannt')
        geburt = getattr(app, 'patient_geburt', '-')

        heute = datetime.now().date()
        zieldatum = heute + timedelta(days=self.tages_offset)

        wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        tag_kurz = wochentage[zieldatum.weekday()]
        datum_str = zieldatum.strftime('%d.%m.%Y')

        if self.tages_offset == 0:
            zusatz = '(heute)'
        elif self.tages_offset == 1:
            zusatz = '(morgen)'
        elif self.tages_offset == -1:
            zusatz = ('gestern')
        else:
            zusatz = f"({self.tages_offset:+d} Tage)"

        plan = getattr(app,'plan_eintraege', [])
        eintraege_heute = [e for e in plan if e.get('tag') == tag_kurz]

        eintraege_heute.sort(key=lambda e: e.get('zeit', ''))

        if eintraege_heute:
            zeilen = []
            for e in eintraege_heute:
                zeit = e.get('zeit', '')
                fach = e.get('fach', '')
                med = e.get('medikament', '')
                anzahl = e.get('anzahl', 1)
                zeilen.append(f"{zeit} | Fach {fach} | {med} (x{anzahl})")
            plan_text = "\n".join(zeilen)
        else:
            plan_text = 'Heute sind keine Einnahmen geplant. '

        eintrag_next, dt_next = app.naechste_einnahme()
        if eintrag_next and dt_next:
            med_next = eintrag_next.get('medikament', '')
            fach_next = eintrag_next.get('fach', '')
            anzahl_next = eintrag_next.get('anzahl', 1)

            next_time_str = dt_next.strftime('%a %d.%m.%Y %H:%M')
            next_line = f'\nNächste Einnahme: {next_time_str} | Fach {fach_next} | {med_next} (x{anzahl_next})'
        else:
            next_line = '\nNächste Einnahme: keine geplant.'

        self. status_label.text = (
            f"Patient: {name}\n"
            f"Geburt: {geburt}\n\n"
            f"Tag: {tag_kurz} {datum_str} {zusatz}\n\n"
            f"{plan_text}"
            f"{next_line}"
        )
        
    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'

    def tag_zurueck(self, instance):
        """Einen Tag zurück blättern."""
        self.tages_offset -= 1
        self.update_status()

    def tag_vor(self, instance):
        """Einen Tag vor blättern."""
        self.tages_offset += 1
        self.update_status()

class PlanListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.anzeige_eintraege = []

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Einnahmeplan',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        scroll = ScrollView(
            size_hint=(1, 0.65)
        )

        self.list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=5
        )

        self.list_layout.bind(
            minimum_height=self.list_layout.setter('height')
        )

        scroll.add_widget(self.list_layout)

        btn_neu = Button(
            text='Neuen Eintrag anlegen',
            size_hint=(1, 0.1)
        )
        btn_neu.bind(on_press=self.neuer_eintrag)

        btn_back = Button(
            text='Zurück zum Hauptmenü',
            size_hint=(1, 0.1)
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        layout.add_widget(titel)
        layout.add_widget(scroll)
        layout.add_widget(btn_neu)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def update_liste(self):
        """Alle Einträge aus der App holen und als Text anzeigen."""
        app = App.get_running_app()
        plan = getattr(app, 'plan_eintraege', [])

        self.list_layout.clear_widgets()
        self.anzeige_eintraege = []

        if not plan:
            hinweis = Label(
                text='Keine Einträge vorhanden.',
                halign='left',
                valign='top',
                size_hint_y=None,
                height=40
            )
            hinweis.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            self.list_layout.add_widget(hinweis)
            return
        
        wochentage_reihenfolge = {
            'Mo': 0, 'Di': 1, 'Mi': 2,
            'Do': 3, 'Fr': 4, 'Sa': 5, 'So': 6
            }

        def sort_key(e):
            tag = e.get('tag', '')
            idx = wochentage_reihenfolge.get(tag, 99)
            zeit = e.get('zeit',  '')
            return (idx, zeit)
        
        plan_sortiert = sorted(plan, key=sort_key)
        self.anzeige_eintraege = plan_sortiert

        for index, e in enumerate(plan_sortiert):
            tag = e.get('tag', '')
            zeit = e.get('zeit', '')
            fach = e.get('fach', '')
            med = e.get('medikament', '')
            anzahl = e.get('anzahl', 1)
            
            text = f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"

            btn = Button(
                text=text,
                size_hint_y=None,
                height=60,
                halign='left'
            )

            btn.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] - 20, None))
            )


            btn.bind(on_press=lambda inst, idx=index: self.eintrag_geklickt(idx))

            self.list_layout.add_widget(btn)

    def eintrag_geklickt(self, index):
        """Wird aufgerufen, wenn ein Eintrag-Button angetippt wird."""
        app = App.get_running_app()

        if index < 0 or index >= len(self.anzeige_eintraege):
            return
        
        eintrag = self.anzeige_eintraege[index]
        med = eintrag.get('medikament', '')
        fach = eintrag.get('fach', '')
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')
        anzahl = eintrag.get('anzahl', 1)

        text = (
            f"{tag} {zeit}\n"
            f"Fach {fach}\n"
            f"{med} (x{anzahl})"
        )

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=text,
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))

        btn_bearbeiten = Button(text='Bearbeiten')
        btn_loeschen = Button(text='Löschen')
        btn_abbrechen = Button(text='Abbrechen')

        btn_layout.add_widget(btn_bearbeiten)
        btn_layout.add_widget(btn_loeschen)
        btn_layout.add_widget(btn_abbrechen)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = Popup(
            title='Eintrag',
            content=layout,
            size_hint=(0.85, 0.5),
            auto_dismiss=False
        )

        def loeschen(_instance):
            try:
                app.plan_eintraege.remove(eintrag)
            except ValueError:
                pass

            app.fach_medikamente = {}
            for e in app.plan_eintraege:
                f = e.get('fach')
                m = e.get('medikament')
                if f and f not in app.fach_medikamente:
                    app.fach_medikamente[f] = m

            app.log_event(
                f"Plan-Eintrag gelöscht: {tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
            )

            app.save_data()
            self.update_liste()
            popup.dismiss()

        def bearbeiten(_instance):
            app = App.get_running_app()
            edit_screen = app.root.get_screen('plan_edit')
            edit_screen.start_bearbeiten(eintrag)
            popup.dismiss()
            app.root.current = 'plan_edit'

        btn_loeschen.bind(on_press=loeschen)
        btn_bearbeiten.bind(on_press=bearbeiten)
        btn_abbrechen.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def neuer_eintrag(self, instance):
        app = App.get_running_app()
        app.root.current = 'plan_edit'

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        app.root.current = 'menu'

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

class SmartMedGUI(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.patient_name = 'Demo-Patient'
        self.patient_geburt = '01.01.2000'
        
        self.plan_eintraege = []
        self.fach_medikamente = {}
        self.log_eintraege = []
        self.offene_einnahmen = []

        self.patient_address = ''
        self.doctor_name = ''
        self.doctor_email = ''
        self.doctor_phone = ''
        self.contact1_name = ''
        self.contact1_email = ''
        self.contact1_phone = ''
        self.contact2_name = ''
        self.contact2_email = ''
        self.contact2_phone = ''

        self.admin_pin = ''

        self.settings  = build_default_settings()

        self.users = {}
        self.current_user = None
        
        self.load_data()

    def _load_user_into_state(self, username):
        """Daten eines Benutzers in die App-Attribute laden"""
        user = self.users.get(username, {})

        self.patient_name = user.get('patient_name', 'Demo-Patient')
        self.patient_geburt = user.get('patient_geburt', '01.01.2000')

        self.patient_address = user.get('patient_address', user.get('patient_adress', ''))
        self.doctor_name = user.get('doctor_name', '')
        self.doctor_email = user.get('doctor_email', '')
        self.doctor_phone = user.get('doctor_phone', '')
        self.contact1_name = user.get('contact1_name', '')
        self.contact1_email = user.get('contact1_email', '')
        self.contact1_phone = user.get('contact1_phone', '')
        self.contact2_name = user.get('contact2_name', '')
        self.contact2_email = user.get('contact2_email', '')
        self.contact2_phone = user.get('contact2_phone', '')

        self.settings.update(user.get('settings', {}))

        self.plan_eintraege = user.get('plan_eintraege', [])
        self.log_eintraege = user.get('log_eintraege', [])

    def _store_current_user_state(self):
        """Aktuelle App-Attribute zurück in das Benutzer-Objekt schreiben."""
        if self.current_user is None:
            return
        
        user = self.users.setdefault(self.current_user, {})

        user.setdefault('password', '')

        user['patient_name'] = self.patient_name
        user['patient_geburt'] = self.patient_geburt

        user['patient_address'] = self.patient_address
        user['doctor_name'] = self.doctor_name
        user['doctor_email'] = self.doctor_email
        user['doctor_phone'] = self.doctor_phone
        user['contact1_name'] = self.contact1_name
        user['contact1_email'] = self.contact1_email
        user['contact1_phone'] = self.contact1_phone
        user['contact2_name'] = self.contact2_name
        user['contact2_email'] = self.contact2_email
        user['contact2_phone'] = self.contact2_phone

        user['settings'] = self.settings.copy()
        user['plan_eintraege'] = self.plan_eintraege
        user['log_eintraege'] = self.log_eintraege

    def switch_user(self, username):
        """Benutzer wechseln undustand laden/speichern."""
        if username not in self.users:
            print(f'Unbekannter Benutzer: {username}')
            return
        
        self._store_current_user_state()

        self.current_user = username
        self._load_user_into_state(username)
        self.save_data()    
        print(f'Benutzer gewechselt zu: {username}')
 
    def load_data(self):
        """Gespeicherte Daten (Users + golbale Fächer) aus JSON laden"""
        data = load_json_data(DATA_FILE)
        if data:
            print(f"Daten aus '{DATA_FILE}' geladen.")

        self.fach_medikamente = data.get('fach_medikamente', {})

        self.admin_pin = data.get('admin_pin', '')

        if 'users' in data:

            self.users = data.get('users', {})
            self.current_user = data.get('current_user')
        else:
            default_user = build_default_user(
                username='Standard',
                password='',
                patient_name=data.get('patient_name', self.patient_name),
                patient_geburt=data.get('patient_geburt', self.patient_geburt),
                settings=data.get('settings', self.settings),
            )
            default_user['plan_eintraege'] = data.get('plan_eintraege', [])
            default_user['log_eintraege'] = data.get('log_eintraege', [])

            self.users = {'Standard': default_user}
            self.current_user = 'Standard'

        if not self.users:
            self.users = {
                'Standard': build_default_user(
                    username='Standard',
                    password='',
                    paatient_name=self.patient_name,
                    patient_geburt=self.patient_geburt,
                    settings=self.settings,
                )
            }
            self.current_user = 'Standard'

        if not self.current_user or self.current_user not in self.users:
            self.current_user = sorted(self.users.keys())[0]

        self._load_user_into_state(self.current_user)
        print(f'Aktueller Benutzer: {self.current_user}')
    
    def save_data(self):
        """Alle Daten (Users " globale Fächer) in JSON speichern."""
        self._store_current_user_state()

        data = {
            'fach_medikamente': self.fach_medikamente,
            'users': self.users,
            'current_user': self.current_user,
            'admin_pin': self.admin_pin,         
        }
        
        save_json_data(DATA_FILE, data)

    def log_event(self, text: str):
        """Einen Log-Eintrag zur Liste inzufügen (ohne sofort zu speichern)."""
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_eintraege.append({'zeit': ts, 'text': text})

        if len(self.log_eintraege) > 1000:
            self.log_eintraege = self.log_eintraege[-1000:]

    def naechste_einnahme(self):
        """Gibt (eintrag, datetime) für die nächste geplante Einnahme zurück."""
        if not self.plan_eintraege:
            return None, None
        
        jetzt = datetime.now()
        wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        heute_index = jetzt.weekday()

        beste_dt = None
        bester_eintrag = None

        for offset in range(0, 7):
            tag_index = (heute_index + offset) % 7
            tag_kurz = wochentage[tag_index]
            datum = jetzt.date() + timedelta(days=offset)

            for e in self.plan_eintraege:
                if e.get('tag') != tag_kurz:
                    continue

                zeit_str = e.get('zeit', '00:00')
                try:
                    stunde, minute = map(int, zeit_str.split(':'))
                except ValueError:
                    continue

                dt = datetime(datum.year, datum.month, datum.day, stunde, minute)

                if dt <= jetzt:
                    continue

                if beste_dt is None or dt < beste_dt:
                    beste_dt = dt
                    bester_eintrag = e

        return bester_eintrag, beste_dt

    def bestaetige_einnahmen(self, due, zeitpunkt):
        """Vom Benutzer bestätigte Einnahmen verarbeiten (loggen, Stepper, ect.)."""
        ts = zeitpunkt.strftime('%Y-%m-%d %H:%M')

        for e in due:
            tag = e.get('tag', '')
            zeit = e.get('zeit', '')
            fach = e.get('fach', '')
            med = e.get('medikament', '')
            anzahl = e.get('anzahl', 1)

            key = (tag, zeit, fach, med)
            for off in self.offene_einnahmen:
                if off.get('key') == key and not off.get('bestaetigt'):
                    off['bestaetigt'] = True

            self.log_event(
                f"Einnahme bestätigt ({ts}): {tag} {zeit} | Fach {fach} | {med} (x{anzahl})")
            
        self.save_data()

    def _zeige_einnahme_popup(self, due, jetzt):
        """Hilfsfunktion: ziegt ein Popup mit den fälligen Einnahmen an."""
        wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        tag_kurz = wochentage[jetzt.weekday()]
        zeit_str = jetzt.strftime('%H:%M')

        zeilen = []
        for e in due:
            fach = e.get('fach', '')
            med = e.get('medikament', '')
            anzahl = e.get('anzahl', 1)
            zeilen.append(f"Fach {fach} | {med} (x{anzahl})")

        einnahmen_text = "\n".join(zeilen)

        text = (
            f"{tag_kurz} {jetzt.strftime('%d.%m.%Y')} {zeit_str}\n\n"
            f"Folgende Einnahme(n) sind fällig:\n\n"
            f"{einnahmen_text}"
        )

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=text,
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_ok = Button(text='Einnahme bestätigen', size_hint=(1, 0.3))

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup = Popup(
            title='Einnahme fällig',
            content=layout,
            size_hint=(0.85, 0.5),
            auto_dismiss=False
        )

        def on_bestaetigen(_instance):
            self.bestaetige_einnahmen(due, jetzt)
            popup.dismiss()

        btn_ok.bind(on_press=on_bestaetigen)

        popup.open()

    def _zeige_alarm_popup(self, eintrag):
        """Popup anzeigen, dass ein Alarm gesendet wurde, weil nicht rechtzeitig bestätigt wurde."""
        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')
        anzahl = eintrag.get('anzahl', 1)
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')

        text = (
            'ALARM wurde gesendet!\n\n'
            'Die Einnahme wurde nicht rechtzeitig bestätigt:\n\n'
            f"{tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
        )

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=text,
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        btn_ok = Button(text='OK', size_hint=(1, 0.3))

        layout.add_widget(label)
        layout.add_widget(btn_ok)

        popup = Popup(
            title='Alarm',
            content=layout,
            size_hint=(0.85, 0.5),
            auto_dismiss=False
        )

        btn_ok.bind(on_press=popup.dismiss)

        popup.open()

    def _auto_pruefen_einnahme(self, dt):
        """Wird regelmässig von Kyvi aufgerufen, prüft ob JETZT Einnahmen fällig sind."""
        if not self.plan_eintraege:
            return
        
        jetzt = datetime.now().replace(second=0, microsecond=0)
        minute_key = jetzt.strftime ('%Y-%m-%d %H:%M')

        if getattr(self, '_last_popup_minute', None) == minute_key:
            return
        
        wochentage = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        tag_kurz = wochentage[jetzt.weekday()]
        zeit_str = jetzt.strftime('%H:%M')

        due = [
            e for e in self.plan_eintraege
            if e.get('tag') == tag_kurz and e.get('zeit') == zeit_str
        ]        

        if not due:
            return
        
        self._last_popup_minute = minute_key

        delay_min = self.settings.get('alarm_delay_min', 30)
        try:
            delay_min = int(delay_min)
            if delay_min <= 0:
                delay_min = 30
        except (TypeError, ValueError):
            delay_min = 30

        deadline = jetzt + timedelta(minutes=delay_min)

        for e in due:
            tag = e.get('tag', tag_kurz)
            zeit = e.get('zeit', zeit_str)
            fach = e.get('fach', '')
            med = e.get('medikament', '')

            key = (tag, zeit, fach, med)

            schon_drin = any(
                (off.get('key') == key) and (not off.get('bestaetigt'))
                for off in self.offene_einnahmen
            )
            if schon_drin:
                continue

            self.offene_einnahmen.append({
                'key': key,
                'eintrag': e,
                'faellige_zeit': jetzt,
                'deadline': deadline,
                'bestaetigt': False,
                'alarm_verschickt': False
            })

        self._zeige_einnahme_popup(due, jetzt)

    def _check_overdue_einnahme(self, dt):
        """Überprüft offene Einnahmen, ob sie überfällig sind, und löst ggf. Alarm aus."""
        if not self.offene_einnahmen:
            return
        
        jetzt = datetime.now()
        for off in self.offene_einnahmen:
            if off.get('bestaetigt'):
                continue
            if off.get('alarm_verschickt'):
                continue

            deadline = off.get('deadline')
            eintrag = off.get('eintrag', {})

            if deadline and jetzt > deadline:
                fach = eintrag.get('fach', '')
                med = eintrag.get('medikament', '')
                anzahl = eintrag.get('anzahl', 1)
                tag = eintrag.get('tag', '')
                zeit = eintrag.get('zeit', '')

                print(
                    f"[ALARM] Einnahme NICHT bestätigt: {tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
                )

                off['alarm_verschickt'] = True

                self.log_event(
                    f"ALARM: Einnahme NICHT bestätigt: {tag} {zeit} | Fach {fach} | {med} (x{anzahl})"
                    )
        
                self.save_data()

                self.sende_alarm_benachrichtigungen(eintrag)

                if self.settings.get('alarm_mode', 'popup') == 'popup':
                    self._zeige_alarm_popup(eintrag)

    def sende_telegram_alarm(self, text):
        """Alarm-text per telegram senden (falls konfiguriert)."""
        chat_id = self.settings.get('telegram_chat_id', '').strip()
        if not TELEGRAM_BOT_TOKEN or not chat_id:
            print('Telegram nicht konfiguriert ( Token oder Chat-ID fehlt).')
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            resp = requests.post(url, data={'chat_id': chat_id, 'text': text})
            if resp.status_code == 200:
                print("Telegram-Alarm gesende.")
                self.log_event('Telegram-Alarm gesendet.')
            else:
                print('Fehler beim Telegram-Request:', resp.text)
                self.log_event(f"Fehler beim Telegram-Request: {resp.text}")
        except Exception as e:
            print("Fehler beim Sendern von Telegram:", e)
            self.log_event(f"Fehler beim Senden vin Telegram: {e}")

    def sende_email_alarm(self, subject, body):
        """Alarm-Mail senden (falls konfiguriert)."""
        to_addr = self.settings.get('email_to', '').strip()
        if not EMAIL_USERNAME or not EMAIL_PASSWORT:
            print('Email nicht konfigurier (Username/Passwort fehlt im Code).')
            return
        if not to_addr:
            print('Keine Empfänger-Adresse (email_to) in den Einstellungen.')
            return
        
        msg= EmailMessage()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP(EMAIL_SMTP_SERVER,EMAIL_SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_USERNAME, EMAIL_PASSWORT)
                smtp.send_message(msg)
            print('Alarm-E_mail gesehndet.')
            self.log_event(f"E-Mail_Alarm an {to_addr} gesendet.")
        except Exception as e:
            print('Fehler beim Senden der E-Mail:', e)
            self.log_event(f"Fehler beim Senden der E-Mail: {e}")

    def sende_alarm_benachrichtigungen(self, eintrag):
        """Je nach Einstellung: E-Mail / Telegram / beides / nichts senden."""
        send_alarm_notifications(
            eintrag=eintrag,
            notify_mode=self.settings.get('notify_mode', 'none'),
            email_to=self.settings.get('email_to', '').strip(),
            telegram_chat_id=self.settings.get('telegram_chat_id', '').strip(),
            telegram_bot_token=TELEGRAM_BOT_TOKEN,
            email_smtp_server=EMAIL_SMTP_SERVER,
            email_smtp_port=EMAIL_SMTP_PORT,
            email_username=EMAIL_USERNAME,
            email_password=EMAIL_PASSWORT,
            log_callback=self.log_event,
        )

    def build(self):
        sm = ScreenManager()

        sm.add_widget(UserLoginScreen(name='login'))
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(StatusScreen(name='status'))
        sm.add_widget(PlanListScreen(name='plan_list'))
        sm.add_widget(LogScreen(name='log'))
        sm.add_widget(PlanEintragErfassenScreen(name='plan_edit'))
        
        sm.add_widget(SettingsMenuScreen(name='settings_menu'))
        sm.add_widget(PatientSettingsScreen(name='settings_patient'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(AdvancedSettingsScreen(name='settings_advanced'))

        sm.current = 'login'

        Clock.schedule_interval(self._auto_pruefen_einnahme, 10.0)
        Clock.schedule_interval(self._check_overdue_einnahme, 60.0)
    
        return sm
    
if __name__ == '__main__':
    SmartMedGUI().run()