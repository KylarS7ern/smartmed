"""Zentraler Einstiegspunkt: die Kivy-App-Klasse und ihre Erzeugung."""

import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from smartmed.config import DATA_FILE, EXPORT_DIR
from smartmed.hardware.serial_transport import create_arduino_transport
from smartmed.models.defaults import build_default_app_state
from smartmed.services.alarm_workflow_service import (
    collect_overdue_alarm_actions,
    execute_alarm_action,
    process_overdue_alarm_actions,
)
from smartmed.services.app_persistence_service import apply_loaded_data, build_data_to_save
from smartmed.services.dispense_service import dispense_slot, ping_arduino
from smartmed.services.event_log_service import (
    append_log_entry,
    export_log_to_file,
    format_log_as_text,
    prune_old_entries,
)
from smartmed.services.hardware_test_workflow_service import run_hardware_test
from smartmed.services.intake_workflow_service import (
    execute_due_intake_workflow,
    prepare_due_intake_workflow,
)
from smartmed.services.notification_service import (
    send_alarm_notifications_for_settings,
    send_late_confirmation_notifications_for_settings,
    send_log_export_email,
)
from smartmed.services.runtime_state_service import reset_runtime_state
from smartmed.services.schedule_service import (
    bereinige_offene_einnahmen,
    berechne_naechste_einnahme,
    bestaetige_offene_einnahmen,
)
from smartmed.services.storage_service import load_json_data, save_json_data
from smartmed.services.user_state_service import load_user_into_app, store_current_user_state
from smartmed.ui.navigation import go_to_menu
from smartmed.ui.popups import (
    show_alarm_popup,
    show_dispense_error_popup,
    show_due_intake_popup,
)
from smartmed.ui.screen_factory import build_screen_manager

# Nach dieser Inaktivität (Sekunden ohne Berührung) kehrt die App vom
# aktuellen Screen automatisch ins Hauptmenü zurück - aber nur auf reinen
# Lese-Screens, nie während einer offenen Eingabemaske (siehe
# _SICHERE_SCREENS_FUER_TIMEOUT), damit nie unbemerkt Eingaben verloren gehen.
_INAKTIVITAETS_TIMEOUT_SEKUNDEN = 300
_SICHERE_SCREENS_FUER_TIMEOUT = {'status', 'log', 'plan_list', 'settings_menu'}


class SmartMedGUI(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        state = build_default_app_state()
        for key, value in state.items():
            setattr(self, key, value)

        self.arduino_transport = create_arduino_transport()
        self._letzte_interaktion = time.monotonic()

        self.load_data()

    def switch_user(self, username):
        """Benutzer wechseln und Zustand laden/speichern."""
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
        self.log_eintraege = prune_old_entries(self.log_eintraege)
        store_current_user_state(self)
        data = build_data_to_save(self)
        save_json_data(DATA_FILE, data)

    def log_event(self, text: str):
        """Fügt einen Log-Eintrag hinzu und speichert die Daten."""
        append_log_entry(self.log_eintraege, text)
        self.save_data()

    def exportiere_log(self):
        """Exportiert das Ereignisprotokoll des aktuellen Benutzers als .txt-Datei."""
        try:
            pfad = export_log_to_file(
                self.log_eintraege,
                EXPORT_DIR,
                patient_name=self.patient_name,
            )
        except OSError as exc:
            return {'ok': False, 'message': f'Export fehlgeschlagen: {exc}'}

        self.log_event(f"Log exportiert nach: {pfad}")
        return {'ok': True, 'message': f'Log exportiert nach:\n{pfad}'}

    def sende_log_per_email(self):
        """Versendet das Ereignisprotokoll des aktuellen Benutzers per E-Mail."""
        to_addr = (self.settings.get('email_to') or '').strip()
        text = format_log_as_text(self.log_eintraege, patient_name=self.patient_name)

        result = send_log_export_email(
            log_text=text,
            to_addr=to_addr,
            log_callback=self.log_event,
        )
        return result

    def ping_arduino_hardware(self):
        return ping_arduino(self.arduino_transport)

    def teste_ausgabe_hardware(self, fach: int, anzahl: int = 1):
        return dispense_slot(self.arduino_transport, slot=fach, count=anzahl)

    def fuehre_hardware_test_aus(self, fach: int = 1, anzahl: int = 1):
        return run_hardware_test(
            transport=self.arduino_transport,
            log_callback=self.log_event,
            fach=fach,
            anzahl=anzahl,
        )

    def naechste_einnahme(self):
        """Gibt (eintrag, datetime) für die nächste geplante Einnahme zurück."""
        return berechne_naechste_einnahme(self.plan_eintraege)

    def bestaetige_einnahmen(self, due, zeitpunkt):
        """Vom Benutzer bestätigte Einnahmen verarbeiten."""
        ergebnis = bestaetige_offene_einnahmen(
            due=due,
            offene_einnahmen=self.offene_einnahmen,
            zeitpunkt=zeitpunkt,
        )

        for text in ergebnis['log_texte']:
            self.log_event(text)

        for eintrag in ergebnis['verspaetet_bestaetigt']:
            self._sende_nachtraegliche_bestaetigung(eintrag)

        self.save_data()

    def _sende_nachtraegliche_bestaetigung(self, eintrag):
        """Löst die zweite Benachrichtigung aus, wenn eine Einnahme erst nach dem Alarm bestätigt wurde."""
        fach = eintrag.get('fach', '')
        med = eintrag.get('medikament', '')
        tag = eintrag.get('tag', '')
        zeit = eintrag.get('zeit', '')

        self.log_event(
            f"Nachträglich bestätigt (nach Alarm): {tag} {zeit} | Fach {fach} | {med}"
        )
        send_late_confirmation_notifications_for_settings(
            eintrag=eintrag,
            settings=self.settings,
            log_callback=self.log_event,
        )

    def _zeige_einnahme_popup(self, due, jetzt):
        """Zeigt das Einnahme-Popup über das UI-Modul an."""
        show_due_intake_popup(
            due=due,
            jetzt=jetzt,
            on_confirm=lambda: self.bestaetige_einnahmen(due, jetzt),
        )

    def _zeige_alarm_popup(self, eintrag):
        """Zeigt das Alarm-Popup über das UI-Modul an."""
        show_alarm_popup(eintrag)

    def _zeige_dispense_fehler_popup(self, failed):
        """Zeigt das Fehler-Popup über das UI-Modul an."""
        show_dispense_error_popup(failed)

    def _auto_pruefen_einnahme(self, dt):
        """Wird regelmässig von Kivy aufgerufen, prüft ob JETZT Einnahmen fällig sind
        und steuert bei Fälligkeit die tatsächliche Ausgabe über den Arduino an."""
        prepared = prepare_due_intake_workflow(
            plan_eintraege=self.plan_eintraege,
            offene_einnahmen=self.offene_einnahmen,
            settings=self.settings,
            last_popup_minute=getattr(self, "_last_popup_minute", None),
        )

        if not prepared:
            return

        self._last_popup_minute = prepared["minute_key"]

        ausgabe = execute_due_intake_workflow(
            transport=self.arduino_transport,
            prepared=prepared,
            offene_einnahmen=self.offene_einnahmen,
        )

        for eintrag in ausgabe["dispensed_eintraege"]:
            fach = eintrag.get("fach", "")
            med = eintrag.get("medikament", "")
            anzahl = eintrag.get("anzahl", 1)
            self.log_event(f"Ausgabe erfolgreich: Fach {fach} | {med} (x{anzahl})")

        for item in ausgabe["failed"]:
            eintrag = item["eintrag"]
            grund = item["result"].get("message", "Unbekannter Fehler.")
            fach = eintrag.get("fach", "")
            med = eintrag.get("medikament", "")
            self.log_event(f"Ausgabe fehlgeschlagen: Fach {fach} | {med} – {grund}")

        if ausgabe["failed"]:
            self._zeige_dispense_fehler_popup(ausgabe["failed"])

        if not ausgabe["dispensed_eintraege"]:
            return

        self.offene_einnahmen.extend(ausgabe["neue_offene"])
        self._zeige_einnahme_popup(ausgabe["dispensed_eintraege"], ausgabe["jetzt"])

    def _check_overdue_einnahme(self, dt):
        """Überprüft offene Einnahmen, ob sie überfällig sind, und löst ggf. Alarm aus."""
        self.offene_einnahmen = bereinige_offene_einnahmen(self.offene_einnahmen)

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

    def _notiere_interaktion(self, *args):
        """Merkt sich den Zeitpunkt der letzten Bildschirm-Berührung (für Inaktivitäts-Timeout)."""
        self._letzte_interaktion = time.monotonic()

    def _pruefe_inaktivitaet(self, dt):
        """Kehrt nach längerer Inaktivität automatisch ins Hauptmenü zurück.

        Wirkt bewusst nur auf reinen Lese-Screens (siehe
        _SICHERE_SCREENS_FUER_TIMEOUT), nie bei einer offenen Eingabemaske
        (Einstellungen, Plan bearbeiten, Login), damit nie unbemerkt
        ungespeicherte Eingaben verloren gehen.
        """
        if self.root is None:
            return

        if self.root.current not in _SICHERE_SCREENS_FUER_TIMEOUT:
            return

        verstrichen = time.monotonic() - self._letzte_interaktion
        if verstrichen >= _INAKTIVITAETS_TIMEOUT_SEKUNDEN:
            go_to_menu(self)
            self._notiere_interaktion()

    def build(self):
        sm = build_screen_manager()

        Clock.schedule_interval(self._auto_pruefen_einnahme, 10.0)
        Clock.schedule_interval(self._check_overdue_einnahme, 60.0)
        Clock.schedule_interval(self._pruefe_inaktivitaet, 30.0)
        Window.bind(on_touch_down=self._notiere_interaktion)

        return sm


def create_app() -> SmartMedGUI:
    """Erstellt die App-Instanz."""
    return SmartMedGUI()
