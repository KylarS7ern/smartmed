from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.hardware.slot_config import SLOT_IDS
from smartmed.ui import theme
from smartmed.ui.navigation import go_to_menu
from smartmed.ui.widgets import (
    BodyLabel,
    MutedLabel,
    PrimaryButton,
    SecondaryButton,
    StyledSpinner,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    make_popup,
)
from smartmed.services.plan_service import (
    TEXT_TO_WIEDERHOLUNG,
    WIEDERHOLUNG_TO_TEXT,
    create_plan_entry,
    update_plan_entry,
)

TAGE = [f'{d:02d}' for d in range(1, 32)]
MONATE = [f'{m:02d}' for m in range(1, 13)]
_AKTUELLES_JAHR = datetime.now().year
JAHRE = [str(j) for j in range(_AKTUELLES_JAHR, _AKTUELLES_JAHR + 6)]

DATE_GROUP_HEIGHT = dp(90)


class PlanEintragErfassenScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bearbeite_eintrag = None

        outer = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Neuer Einnahme-Eintrag',
            font_size=theme.FONT_XLARGE,
            size_hint=(1, None),
            height=dp(48)
        )

        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation='vertical', spacing=theme.SPACING, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.med_input = StyledTextInput(
            hint_text='Medikamentenname',
            multiline=False,
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )

        self.fach_spinner = StyledSpinner(
            text='Fach wählen',
            values=tuple(str(slot_id) for slot_id in SLOT_IDS),
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )

        self.fach_info_label = MutedLabel(
            text='Fach: (noch nichts gewählt)',
            size_hint=(1, None),
            height=dp(32)
        )

        self.fach_spinner.bind(text=self.on_fach_gewaehlt)

        self.wiederholung_spinner = StyledSpinner(
            text='Wöchentlich',
            values=('Wöchentlich', 'Täglich', 'Einmalig'),
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )
        self.wiederholung_spinner.bind(text=self._aktualisiere_wiederholung_sichtbarkeit)

        self.tag_spinner = StyledSpinner(
            text='Wochentag wählen',
            values=('Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'),
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )

        (
            self.einmalig_gruppe,
            self.einmalig_tag_spinner,
            self.einmalig_monat_spinner,
            self.einmalig_jahr_spinner,
        ) = self._build_date_group('Datum der einmaligen Einnahme:')

        (
            self.bis_gruppe,
            self.bis_tag_spinner,
            self.bis_monat_spinner,
            self.bis_jahr_spinner,
        ) = self._build_date_group('Enddatum (optional, leer = ohne Ende):')

        self.anzahl_spinner = StyledSpinner(
            text='Anzahl Pillen',
            values=('1', '2', '3', '4', '5'),
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.ROW_HEIGHT
        )

        stunden = [f'{h:02d}' for h in range(0, 24)]
        minuten = [f'{m:02d}' for m in range(0, 60, 5)]

        uhrzeit_layout = BoxLayout(
            orientation='horizontal', spacing=theme.SPACING,
            size_hint=(1, None), height=theme.ROW_HEIGHT
        )

        self.stunde_spinner = StyledSpinner(
            text='Stunde',
            values=tuple(stunden),
            font_size=theme.FONT_LARGE,
            size_hint=(0.5, 1)
        )

        self.minute_spinner = StyledSpinner(
            text='Minute',
            values=tuple(minuten),
            font_size=theme.FONT_LARGE,
            size_hint=(0.5, 1)
        )

        uhrzeit_layout.add_widget(self.stunde_spinner)
        uhrzeit_layout.add_widget(self.minute_spinner)

        btn_speichern = SuccessButton(
            text='Eintrag speichern',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_speichern.bind(on_press=self.speichern_eintrag)

        btn_back = SecondaryButton(
            text='Zurück zum Hauptmenü',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck_zum_menue)

        form.add_widget(self.med_input)
        form.add_widget(self.fach_spinner)
        form.add_widget(self.fach_info_label)
        form.add_widget(self.wiederholung_spinner)
        form.add_widget(self.tag_spinner)
        form.add_widget(self.einmalig_gruppe)
        form.add_widget(self.bis_gruppe)
        form.add_widget(self.anzahl_spinner)
        form.add_widget(uhrzeit_layout)

        scroll.add_widget(form)

        outer.add_widget(titel)
        outer.add_widget(scroll)
        outer.add_widget(btn_speichern)
        outer.add_widget(btn_back)

        self.add_widget(outer)

        self._aktualisiere_wiederholung_sichtbarkeit()

    def _build_date_group(self, label_text):
        """Baut eine label + Tag/Monat/Jahr-Spinner-Gruppe für Datumsauswahl."""
        gruppe = BoxLayout(
            orientation='vertical', spacing=dp(4),
            size_hint=(1, None), height=DATE_GROUP_HEIGHT
        )

        label = MutedLabel(text=label_text, size_hint=(1, None), height=dp(28))

        reihe = BoxLayout(orientation='horizontal', spacing=theme.SPACING, size_hint=(1, None), height=theme.ROW_HEIGHT)
        tag_spinner = StyledSpinner(text='Tag', values=tuple(TAGE), font_size=theme.FONT_BODY, size_hint=(0.34, 1))
        monat_spinner = StyledSpinner(text='Monat', values=tuple(MONATE), font_size=theme.FONT_BODY, size_hint=(0.34, 1))
        jahr_spinner = StyledSpinner(text='Jahr', values=tuple(JAHRE), font_size=theme.FONT_BODY, size_hint=(0.32, 1))

        reihe.add_widget(tag_spinner)
        reihe.add_widget(monat_spinner)
        reihe.add_widget(jahr_spinner)

        gruppe.add_widget(label)
        gruppe.add_widget(reihe)

        return gruppe, tag_spinner, monat_spinner, jahr_spinner

    def _set_gruppe_sichtbar(self, gruppe, sichtbar):
        gruppe.height = DATE_GROUP_HEIGHT if sichtbar else 0
        gruppe.opacity = 1 if sichtbar else 0
        gruppe.disabled = not sichtbar

    def _set_spinner_sichtbar(self, spinner, sichtbar):
        spinner.height = theme.ROW_HEIGHT if sichtbar else 0
        spinner.opacity = 1 if sichtbar else 0
        spinner.disabled = not sichtbar

    def _aktualisiere_wiederholung_sichtbarkeit(self, *_args):
        modus = self.wiederholung_spinner.text
        ist_woechentlich = modus == 'Wöchentlich'
        ist_taeglich = modus == 'Täglich'
        ist_einmalig = modus == 'Einmalig'

        self._set_spinner_sichtbar(self.tag_spinner, ist_woechentlich)
        self._set_gruppe_sichtbar(self.einmalig_gruppe, ist_einmalig)
        self._set_gruppe_sichtbar(self.bis_gruppe, ist_woechentlich or ist_taeglich)

    def zeige_meldung(self, text):
        """zeigt eine einfache Hinweis-Popup-Meldung an."""
        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=text,
            halign='center',
            valign='middle'
        )

        btn_ok = PrimaryButton(
            text='OK',
            size_hint=(1, 0.3)
        )

        popup = make_popup(title='Hinweis', content=layout, size_hint=(0.8, 0.4))

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

    def _lese_datum_gruppe(self, tag_spinner, monat_spinner, jahr_spinner):
        """Liest eine Tag/Monat/Jahr-Spinner-Gruppe.

        Gibt ('leer', None), ('unvollstaendig', None) oder
        ('vollstaendig', 'TT.MM.JJJJ') zurück.
        """
        tag = tag_spinner.text.strip()
        monat = monat_spinner.text.strip()
        jahr = jahr_spinner.text.strip()

        tag_leer = tag == 'Tag'
        monat_leer = monat == 'Monat'
        jahr_leer = jahr == 'Jahr'

        if tag_leer and monat_leer and jahr_leer:
            return 'leer', None

        if tag_leer or monat_leer or jahr_leer:
            return 'unvollstaendig', None

        return 'vollstaendig', f'{tag}.{monat}.{jahr}'

    def _setze_datum_gruppe(self, datum_str, tag_spinner, monat_spinner, jahr_spinner):
        if not datum_str:
            return
        try:
            tag, monat, jahr = datum_str.split('.')
        except ValueError:
            return
        if tag in tag_spinner.values:
            tag_spinner.text = tag
        if monat in monat_spinner.values:
            monat_spinner.text = monat
        if jahr in jahr_spinner.values:
            jahr_spinner.text = jahr

    def _reset_datum_gruppe(self, tag_spinner, monat_spinner, jahr_spinner):
        tag_spinner.text = 'Tag'
        monat_spinner.text = 'Monat'
        jahr_spinner.text = 'Jahr'

    def speichern_eintrag(self, instance):
        """Einen neuen Eintrag speichern oder bestehenden Eintrag aktualisieren."""
        app = App.get_running_app()

        med = self.med_input.text.strip()
        fach = self.fach_spinner.text.strip()
        anzahl = self.anzahl_spinner.text.strip()
        stunde = self.stunde_spinner.text.strip()
        minute = self.minute_spinner.text.strip()
        wiederholung_text = self.wiederholung_spinner.text.strip()
        wiederholung = TEXT_TO_WIEDERHOLUNG.get(wiederholung_text, 'woechentlich')

        if (
            not med or
            fach.startswith('Fach') or
            anzahl.startswith('Anzahl') or
            stunde == 'Stunde' or
            minute == 'Minute'
        ):
            self.zeige_meldung('Bitte alle Felder auswählen/ausfüllen.')
            return

        tag = None
        datum = None
        bis_datum = None

        if wiederholung == 'einmalig':
            status, wert = self._lese_datum_gruppe(
                self.einmalig_tag_spinner, self.einmalig_monat_spinner, self.einmalig_jahr_spinner
            )
            if status != 'vollstaendig':
                self.zeige_meldung('Bitte ein vollständiges Datum für die einmalige Einnahme auswählen.')
                return
            datum = wert
        else:
            if wiederholung == 'woechentlich':
                tag = self.tag_spinner.text.strip()
                if tag.startswith('Wochentag'):
                    self.zeige_meldung('Bitte einen Wochentag auswählen.')
                    return

            status, wert = self._lese_datum_gruppe(
                self.bis_tag_spinner, self.bis_monat_spinner, self.bis_jahr_spinner
            )
            if status == 'unvollstaendig':
                self.zeige_meldung('Bitte das Enddatum vollständig ausfüllen oder komplett leer lassen.')
                return
            bis_datum = wert

        zeit = f'{stunde}:{minute}'
        anzahl_int = int(anzahl)

        if self.bearbeite_eintrag is not None:
            result = update_plan_entry(
                plan_eintraege=app.plan_eintraege,
                fach_medikamente=app.fach_medikamente,
                eintrag=self.bearbeite_eintrag,
                medikament=med,
                fach=fach,
                zeit=zeit,
                anzahl=anzahl_int,
                wiederholung=wiederholung,
                tag=tag,
                datum=datum,
                bis_datum=bis_datum,
            )
        else:
            result = create_plan_entry(
                plan_eintraege=app.plan_eintraege,
                fach_medikamente=app.fach_medikamente,
                medikament=med,
                fach=fach,
                zeit=zeit,
                anzahl=anzahl_int,
                wiederholung=wiederholung,
                tag=tag,
                datum=datum,
                bis_datum=bis_datum,
            )

        if not result['ok']:
            self.zeige_meldung(result['message'])

            prefill_medikament = result.get('prefill_medikament')
            if prefill_medikament:
                self.med_input.text = prefill_medikament

            return

        app.fach_medikamente = result['fach_medikamente']
        app.log_event(result['log_text'])
        self.felder_zuruecksetzen()

    def felder_zuruecksetzen(self):
        """Eingabefelder wieder in Grundzustand setzen."""
        self.bearbeite_eintrag = None
        self.med_input.text = ''
        self.fach_spinner.text = 'Fach wählen'
        self.fach_info_label.text = 'Fach: (noch nichts gewählt)'
        self.wiederholung_spinner.text = 'Wöchentlich'
        self.tag_spinner.text = 'Wochentag wählen'
        self.anzahl_spinner.text = 'Anzahl Pillen'
        self.stunde_spinner.text = 'Stunde'
        self.minute_spinner.text = 'Minute'
        self._reset_datum_gruppe(self.einmalig_tag_spinner, self.einmalig_monat_spinner, self.einmalig_jahr_spinner)
        self._reset_datum_gruppe(self.bis_tag_spinner, self.bis_monat_spinner, self.bis_jahr_spinner)
        self._aktualisiere_wiederholung_sichtbarkeit()

    def start_bearbeiten(self, eintrag):
        """Bestehenden Eintrag in die Felder laden und Bearbeitungsmodus aktivieren."""
        self.bearbeite_eintrag = eintrag

        med = eintrag.get('medikament', '')
        fach = eintrag.get('fach', '')
        zeit = eintrag.get('zeit', '')
        anzahl = eintrag.get('anzahl', 1)
        wiederholung = eintrag.get('wiederholung', 'woechentlich')

        try:
            stunde, minute = zeit.split(':')
        except ValueError:
            stunde, minute = '00', '00'

        self.med_input.text = med
        self.fach_spinner.text = fach
        self.anzahl_spinner.text = str(anzahl)
        self.stunde_spinner.text = stunde
        self.minute_spinner.text = minute
        self.wiederholung_spinner.text = WIEDERHOLUNG_TO_TEXT.get(wiederholung, 'Wöchentlich')

        self._reset_datum_gruppe(self.einmalig_tag_spinner, self.einmalig_monat_spinner, self.einmalig_jahr_spinner)
        self._reset_datum_gruppe(self.bis_tag_spinner, self.bis_monat_spinner, self.bis_jahr_spinner)

        if wiederholung == 'einmalig':
            self.tag_spinner.text = 'Wochentag wählen'
            self._setze_datum_gruppe(
                eintrag.get('datum', ''),
                self.einmalig_tag_spinner, self.einmalig_monat_spinner, self.einmalig_jahr_spinner
            )
        else:
            self.tag_spinner.text = eintrag.get('tag') or 'Wochentag wählen'
            self._setze_datum_gruppe(
                eintrag.get('bis_datum', ''),
                self.bis_tag_spinner, self.bis_monat_spinner, self.bis_jahr_spinner
            )

        self._aktualisiere_wiederholung_sichtbarkeit()

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)
