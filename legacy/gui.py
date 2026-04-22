from smartmed.config import DATA_FILE

from smartmed.hardware.serial_transport import ArduinoSerialTransport

from smartmed.services.hardware_test_workflow_service import run_hardware_test
from smartmed.services.dispense_service import dispense_slot, ping_arduino
from smartmed.services.storage_service import load_json_data, save_json_data
from smartmed.services.user_state_service import load_user_into_app, store_current_user_state
from smartmed.services.app_persistence_service import apply_loaded_data, build_data_to_save
from smartmed.services.event_log_service import append_log_entry
from smartmed.services.intake_workflow_service import prepare_due_intake_workflow
from smartmed.services.notification_service import send_alarm_notifications_for_settings
from smartmed.services.alarm_workflow_service import (
    collect_overdue_alarm_actions, 
    process_overdue_alarm_actions,
    execute_alarm_action,
    )
from smartmed.services.runtime_state_service import reset_runtime_state

from smartmed.models.defaults import build_default_settings, build_default_user, build_default_app_state

from smartmed.ui.screens.status_screen import StatusScreen
from smartmed.ui.screens.log_screen import LogScreen
from smartmed.ui.screens.main_menu_screen import MainMenuScreen
from smartmed.ui.screens.settings_menu_screen import SettingsMenuScreen
from smartmed.ui.screens.plan_list_screen import PlanListScreen
from smartmed.ui.screens.user_login_screen import UserLoginScreen
from smartmed.ui.screens.patient_settings_screen import PatientSettingsScreen
from smartmed.ui.screens.advanced_settings_screen import AdvancedSettingsScreen
from smartmed.ui.screens.settings_screen import SettingsScreen
from smartmed.ui.screens.plan_edit_screen import PlanEintragErfassenScreen
from smartmed.ui.screen_factory import build_screen_manager
from smartmed.ui.popups import show_due_intake_popup, show_alarm_popup



from smartmed.services.schedule_service import (
    berechne_naechste_einnahme,
    bestaetige_offene_einnahmen,    
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

class SmartMedGUI(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        state = build_default_app_state()
        for key, value in state.items():
            setattr(self, key, value)
        
        self.arduino_transport = ArduinoSerialTransport()

        self.load_data()

    def switch_user(self, username):
        """Benutzer wechseln undustand laden/speichern."""
        if username not in self.users:
            print(f'Unbekannter Benutzer: {username}')
            return
        
        store_current_user_state(self)

        self.current_user = username
        load_user_into_app(self, username)
        reset_runtime_state(self)
        self.save_data()
        print(f'Benutzer gewechselt zu: {username}')
 
    def load_data(self):
        """Gespeicherte Daten (Users + globale Fächer) aus JSON laden"""
        data = load_json_data(DATA_FILE)
        if data:
            print(f"Daten aus '{DATA_FILE}' geladen.")

        apply_loaded_data(self, data)
        load_user_into_app(self, self.current_user)
        reset_runtime_state(self)
        print(f'Aktueller Benutzer: {self.current_user}')

    def save_data(self):
        """Alle Daten (Users + globale Fächer) in JSON speichern."""
        store_current_user_state(self)
        data = build_data_to_save(self)
        save_json_data(DATA_FILE, data)

    def log_event(self, text: str):
        """Fügt einen Log-Eintrag hinzu und speichert die Daten."""
        append_log_entry(self.log_eintraege, text)
        self.save_data()

    def ping_arduino_hardware(self):
        return ping_arduino(self.arduino_transport)

    def teste_ausgabe_hardware(self, fach: int, anzahl: int = 1):
        return dispense_slot(self.arduino_transport, slot=fach, count=anzahl)

    def fuehre_hardware_test_aus(self, fach: int = 1, anzahl: int = 1):
        ping_result = self.ping_arduino_hardware()
        if not ping_result.get("ok"):
            message = ping_result.get("message", "Arduino nicht erreichbar.")
            self.log_event(f"Hardware-Test fehlgeschlagen: {message}")
            return {
                "ok": False,
                "kind": "ping_failed",
                "message": message,
                "ping_result": ping_result,
            }

        dispense_result = self.teste_ausgabe_hardware(fach=fach, anzahl=anzahl)
        if dispense_result.get("ok"):
            self.log_event(
                f"Hardware-Test erfolgreich: Fach {fach}, Anzahl {anzahl}."
            )
            return {
                "ok": True,
                "kind": "hardware_test_success",
                "message": f"Hardware-Test erfolgreich für Fach {fach}.",
                "ping_result": ping_result,
                "dispense_result": dispense_result,
            }

        message = dispense_result.get("message", "Unbekannter Hardware-Fehler.")
        self.log_event(
            f"Hardware-Test fehlgeschlagen bei Fach {fach}, Anzahl {anzahl}: {message}"
        )
        return {
            "ok": False,
            "kind": "dispense_failed",
            "message": message,
            "ping_result": ping_result,
            "dispense_result": dispense_result,
        }


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
        """Zeigt das Einnahme-Popup über das neue UI-Modul an."""
        show_due_intake_popup(
            due=due,
            jetzt=jetzt,
            on_confirm=lambda: self.bestaetige_einnahmen(due, jetzt),
        )
   
    def _zeige_alarm_popup(self, eintrag):
        """Zeigt das Alarm-Popup über das neue UI-Modul an."""
        show_alarm_popup(eintrag)

    def _auto_pruefen_einnahme(self, dt):
        """Wird regelmässig von Kivy aufgerufen, prüft ob JETZT Einnahmen fällig sind."""
        result = prepare_due_intake_workflow(
            plan_eintraege=self.plan_eintraege,
            offene_einnahmen=self.offene_einnahmen,
            settings=self.settings,
            last_popup_minute=getattr(self, "_last_popup_minute", None),
        )

        if not result:
            return

        self._last_popup_minute = result["minute_key"]
        self.offene_einnahmen.extend(result["neue_offene"])
        self._zeige_einnahme_popup(result["due"], result["jetzt"])
        
    def _check_overdue_einnahme(self, dt):
        """Überprüft offene Einnahmen, ob sie überfällig sind, und löst ggf. Alarm aus."""
        verarbeitete = collect_overdue_alarm_actions(self.offene_einnahmen)

        if not verarbeitete:
            return

        self._verarbeite_ueberfaellige_einnahmen(verarbeitete)

    def _verarbeite_ueberfaellige_einnahmen(self, verarbeitete):
        """Verarbeitet überfällige Einnahmen und löst Alarm-Aktionen aus."""
        process_overdue_alarm_actions(
            verarbeitete,
            trigger_alarm_callback=self._loese_nicht_bestaetigt_alarm_aus,
        )
        
    def sende_alarm_benachrichtigungen(self, eintrag):
        """Alarm-Benachrichtigungen gemäss aktuellen Einstellungen senden."""
        send_alarm_notifications_for_settings(
            eintrag=eintrag,
            settings=self.settings,
            log_callback=self.log_event,
        )

    def _loese_nicht_bestaetigt_alarm_aus(self, eintrag, console_text, log_text):
        """Löst Alarm für eine nicht bestätigte Einnahme aus."""
        execute_alarm_action(
            eintrag=eintrag,
            console_text=console_text,
            log_text=log_text,
            log_callback=self.log_event,
            notify_callback=self.sende_alarm_benachrichtigungen,
            popup_callback=self._zeige_alarm_popup,
            save_callback=self.save_data,
        )

    def build(self):
        sm = build_screen_manager()

        Clock.schedule_interval(self._auto_pruefen_einnahme, 10.0)
        Clock.schedule_interval(self._check_overdue_einnahme, 60.0)

        return sm

if __name__ == '__main__':
    SmartMedGUI().run()