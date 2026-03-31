from smartmed.config import DATA_FILE
from smartmed.services.storage_service import load_json_data, save_json_data
from smartmed.models.defaults import build_default_settings, build_default_user
from smartmed.services.notification_service import send_alarm_notifications
from smartmed.ui.screens.status_screen import StatusScreen
from smartmed.ui.screens.log_screen import LogScreen
from smartmed.ui.screens.main_menu_screen import MainMenuScreen
from smartmed.ui.screens.settings_menu_screen import SettingsMenuScreen
from smartmed.ui.screens.plan_list_screen import PlanListScreen
from smartmed.ui.screens.user_login_screen import UserLoginScreen
from smartmed.ui.screens.start_screen import StartScreen
from smartmed.ui.screens.patient_settings_screen import PatientSettingsScreen
from smartmed.ui.screens.advanced_settings_screen import AdvancedSettingsScreen
from smartmed.ui.screens.settings_screen import SettingsScreen
from smartmed.ui.screens.plan_edit_screen import PlanEintragErfassenScreen
from smartmed.ui.screen_factory import build_screen_manager

from smartmed.services.schedule_service import (
    berechne_alarm_delay_minuten,
    berechne_naechste_einnahme,
    bestaetige_offene_einnahmen,
    erstelle_offene_einnahmen,
    finde_faellige_einnahmen,
    finde_ueberfaellige_offene_einnahmen,
)



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
        return berechne_naechste_einnahme(self.plan_eintraege)

    def bestaetige_einnahmen(self, due, zeitpunkt):
        """Vom Benutzer bestätigte Einnahmen verarbeiten."""
        log_texte = bestaetige_offene_einnahmen(
            due=due,
            offene_einnahmen=self.offene_einnahmen,
            zeitpunkt=zeitpunkt,
        )

        for text in log_texte:
            self.log_event(text)

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
        """Wird regelmässig von Kivy aufgerufen, prüft ob JETZT Einnahmen fällig sind."""
        if not self.plan_eintraege:
            return

        due, jetzt, minute_key, tag_kurz, zeit_str = finde_faellige_einnahmen(
            self.plan_eintraege
        )

        if getattr(self, '_last_popup_minute', None) == minute_key:
            return

        if not due:
            return

        self._last_popup_minute = minute_key

        delay_min = berechne_alarm_delay_minuten(
            self.settings.get('alarm_delay_min', 30)
        )

        neue_offene = erstelle_offene_einnahmen(
            due=due,
            offene_einnahmen=self.offene_einnahmen,
            jetzt=jetzt,
            delay_min=delay_min,
            tag_kurz=tag_kurz,
            zeit_str=zeit_str,
        )
        self.offene_einnahmen.extend(neue_offene)

        self._zeige_einnahme_popup(due, jetzt)
    
    def _check_overdue_einnahme(self, dt):
        """Überprüft offene Einnahmen, ob sie überfällig sind, und löst ggf. Alarm aus."""
        if not self.offene_einnahmen:
            return

        ueberfaellige, jetzt = finde_ueberfaellige_offene_einnahmen(
            self.offene_einnahmen
        )

        if not ueberfaellige:
            return

        for off in ueberfaellige:
            eintrag = off.get('eintrag', {})

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
        sm = build_screen_manager()

        Clock.schedule_interval(self._auto_pruefen_einnahme, 10.0)
        Clock.schedule_interval(self._check_overdue_einnahme, 60.0)

        return sm
    
if __name__ == '__main__':
    SmartMedGUI().run()