from threading import Thread

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from smartmed.hardware.slot_config import get_slot_label
from smartmed.ui import theme
from smartmed.ui.navigation import go_to_settings_menu
from smartmed.ui.widgets import (
    BodyLabel,
    DangerButton,
    MutedLabel,
    PrimaryButton,
    SecondaryButton,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    WarningButton,
    field_row,
    make_popup,
)
from smartmed.services.admin_pin_service import (
    build_admin_pin_status_text,
    build_admin_pin_update,
)


class AdvancedSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        outer = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Erweiterte Einstellungen',
            font_size=theme.FONT_XLARGE,
            size_hint=(1, None),
            height=dp(48)
        )

        scroll = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=theme.SPACING, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        info = MutedLabel(
            text=(
                'Hier kommen später weitere globale Einstellungen hin,\n'
                'z.B. WLAN, Zeitsynchronisation, Fach-Medikament.'
            ),
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(70)
        )

        self.pin_info_label = MutedLabel(
            text='',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(36)
        )

        self.hardware_test_label = MutedLabel(
            text='Hardware-Test noch nicht ausgeführt.',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(36)
        )

        self.pin_input = StyledTextInput(
            multiline=False,
            password=True,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )
        self.pin_repeat_input = StyledTextInput(
            multiline=False,
            password=True,
            font_size=theme.FONT_BODY,
            size_hint=(0.5, 1)
        )

        btn_save_pin = SuccessButton(
            text='Admin-PIN speichern / entfernen',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_save_pin.bind(on_press=self.speichern_pin)

        btn_test_fach_1 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(1)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_1.bind(on_press=self.hardware_test_fach_1)

        btn_test_fach_2 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(2)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_2.bind(on_press=self.hardware_test_fach_2)

        btn_test_fach_3 = WarningButton(
            text=f'Hardware-Test: {get_slot_label(3)} einmal ausgeben',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_test_fach_3.bind(on_press=self.hardware_test_fach_3)

        self.hardware_test_buttons = [
            btn_test_fach_1,
            btn_test_fach_2,
            btn_test_fach_3,
        ]

        backup_titel = BodyLabel(
            text='Datensicherung (alle Benutzer, Pläne, Logs):',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=dp(36)
        )

        self.backup_status_label = MutedLabel(
            text='',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(50)
        )

        btn_backup_export = SuccessButton(
            text='Datensicherung exportieren',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_backup_export.bind(on_press=self.backup_exportieren)

        btn_backup_email = SuccessButton(
            text='Sicherung per E-Mail senden',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_backup_email.bind(on_press=self.backup_per_email_senden)

        btn_backup_restore = DangerButton(
            text='Sicherung wiederherstellen...',
            font_size=theme.FONT_BODY,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_backup_restore.bind(on_press=self.backup_wiederherstellen_anfragen)

        btn_back = SecondaryButton(
            text='Zurück',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(info)
        layout.add_widget(self.pin_info_label)
        layout.add_widget(self.hardware_test_label)
        layout.add_widget(field_row('Neuer Admin-PIN:', self.pin_input))
        layout.add_widget(field_row('PIN wiederholen:', self.pin_repeat_input))
        layout.add_widget(btn_save_pin)
        layout.add_widget(btn_test_fach_1)
        layout.add_widget(btn_test_fach_2)
        layout.add_widget(btn_test_fach_3)
        layout.add_widget(backup_titel)
        layout.add_widget(self.backup_status_label)
        layout.add_widget(btn_backup_export)
        layout.add_widget(btn_backup_email)
        layout.add_widget(btn_backup_restore)

        scroll.add_widget(layout)

        outer.add_widget(titel)
        outer.add_widget(scroll)
        outer.add_widget(btn_back)

        self.add_widget(outer)

    def on_pre_enter(self, *args):
        """Status anzeigen, wenn Screen geöffnet wird."""
        app = App.get_running_app()
        self.pin_info_label.text = build_admin_pin_status_text(
            getattr(app, 'admin_pin', '')
        )
        self.pin_input.text = ''
        self.pin_repeat_input.text = ''
        self.hardware_test_label.text = 'Hardware-Test noch nicht ausgeführt.'
        self._set_hardware_test_buttons_enabled(True)
        self.backup_status_label.text = ''

    def speichern_pin(self, instance):
        """Admin-PIN speichern oder entfernen."""
        app = App.get_running_app()

        result = build_admin_pin_update(
            self.pin_input.text,
            self.pin_repeat_input.text,
        )

        if not result['ok']:
            self.pin_info_label.text = result['message']
            return

        app.admin_pin = result['admin_pin']
        app.save_data()
        self.pin_info_label.text = result['message']

    def _set_hardware_test_buttons_enabled(self, enabled: bool):
        for button in self.hardware_test_buttons:
            button.disabled = not enabled

    def hardware_test_fach(self, fach: int):
        self._set_hardware_test_buttons_enabled(False)
        self.hardware_test_label.text = (
            f'Hardware-Test für {get_slot_label(fach)} startet in 1 Sekunde...'
        )
        Clock.schedule_once(
            lambda dt: self._starte_hardware_test_im_hintergrund(fach),
            1.0
        )

    def _starte_hardware_test_im_hintergrund(self, fach: int):
        # Eine echte Ausgabe lässt den Arduino mehrere Sekunden am Motor
        # drehen, bevor er antwortet - ohne eigenen Thread würde die
        # gesamte App (Touch, Uhrzeit, Timer) für diese Zeit einfrieren.
        Thread(
            target=self._run_hardware_test_worker,
            args=(fach,),
            daemon=True,
        ).start()

    def _run_hardware_test_worker(self, fach: int):
        try:
            app = App.get_running_app()
            result = app.fuehre_hardware_test_aus(fach=fach, anzahl=1)
        except Exception as exc:
            result = {
                'message': f'Unerwarteter Fehler beim Hardware-Test: {exc}'
            }

        Clock.schedule_once(
            lambda dt: self._verarbeite_hardware_test_ergebnis(result),
            0
        )

    def _verarbeite_hardware_test_ergebnis(self, result: dict):
        self.hardware_test_label.text = result.get(
            'message',
            'Unbekanntes Ergebnis beim Hardware-Test.'
        )
        self._set_hardware_test_buttons_enabled(True)

    def hardware_test_fach_1(self, instance):
        self.hardware_test_fach(1)

    def hardware_test_fach_2(self, instance):
        self.hardware_test_fach(2)

    def hardware_test_fach_3(self, instance):
        self.hardware_test_fach(3)

    def backup_exportieren(self, instance):
        app = App.get_running_app()
        result = app.exportiere_backup()
        self.backup_status_label.text = result.get('message', '')

    def backup_per_email_senden(self, instance):
        app = App.get_running_app()
        result = app.sende_backup_per_email()
        self.backup_status_label.text = result.get('message', '')

    def backup_wiederherstellen_anfragen(self, instance):
        """Zeigt die vorhandenen Sicherungsdateien zur Auswahl an."""
        app = App.get_running_app()
        dateien = app.liste_backups()

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        if not dateien:
            label = BodyLabel(
                text='Keine Sicherungsdateien im Exportordner gefunden.',
                halign='center',
                valign='middle'
            )
            btn_ok = PrimaryButton(text='OK', size_hint=(1, 0.3))
            layout.add_widget(label)
            layout.add_widget(btn_ok)
            popup = make_popup(title='Sicherung wiederherstellen', content=layout, size_hint=(0.85, 0.4))
            btn_ok.bind(on_press=lambda *_: popup.dismiss())
            popup.open()
            return

        label = BodyLabel(
            text='Welche Sicherung wiederherstellen?',
            halign='center',
            valign='middle',
            size_hint=(1, 0.2)
        )

        scroll = ScrollView(size_hint=(1, 0.6))
        liste = BoxLayout(orientation='vertical', spacing=theme.SPACING, size_hint_y=None)
        liste.bind(minimum_height=liste.setter('height'))

        for pfad in dateien:
            btn = PrimaryButton(
                text=pfad.name,
                font_size=theme.FONT_SMALL,
                size_hint_y=None,
                height=dp(56)
            )
            btn.bind(on_press=lambda inst, p=pfad: self._backup_auswaehlen(popup, p))
            liste.add_widget(btn)

        scroll.add_widget(liste)

        btn_abbrechen = SecondaryButton(text='Abbrechen', size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(scroll)
        layout.add_widget(btn_abbrechen)

        popup = make_popup(title='Sicherung wiederherstellen', content=layout, size_hint=(0.9, 0.8))
        btn_abbrechen.bind(on_press=lambda *_: popup.dismiss())
        popup.open()

    def _backup_auswaehlen(self, liste_popup, pfad):
        liste_popup.dismiss()
        self._zeige_restore_bestaetigung(pfad)

    def _zeige_restore_bestaetigung(self, pfad):
        """Starke Sicherheitsabfrage, da die Wiederherstellung alle aktuellen Daten ersetzt."""
        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=(
                f'"{pfad.name}" wirklich wiederherstellen?\n\n'
                'ALLE aktuellen Daten (alle Benutzer, Pläne, Logs) werden dabei '
                'unwiderruflich durch den Inhalt dieser Sicherung ersetzt.'
            ),
            halign='center',
            valign='middle'
        )

        btn_layout = BoxLayout(orientation='horizontal', spacing=theme.SPACING, size_hint=(1, 0.3))

        btn_ja = DangerButton(text='Ja, ersetzen')
        btn_nein = SecondaryButton(text='Nein')

        btn_layout.add_widget(btn_ja)
        btn_layout.add_widget(btn_nein)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Wiederherstellung bestätigen', content=layout, size_hint=(0.9, 0.6))

        def ja(_instance):
            popup.dismiss()
            self._backup_wiederherstellen(pfad)

        btn_ja.bind(on_press=ja)
        btn_nein.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def _backup_wiederherstellen(self, pfad):
        app = App.get_running_app()
        result = app.stelle_backup_wieder_her(pfad)
        self.backup_status_label.text = result.get('message', '')
        self.pin_info_label.text = build_admin_pin_status_text(
            getattr(app, 'admin_pin', '')
        )

    def zurueck(self, instance):
        app = App.get_running_app()
        go_to_settings_menu(app)
