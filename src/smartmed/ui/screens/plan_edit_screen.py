from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


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

        stunden = [f'{h:02d}' for h in range(0, 24)]
        minuten = [f'{m:02d}' for m in range(0, 60, 5)]

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

        btn_back = Button(
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
        """Einen neuen Eintrag speichern oder bestehenden Eintrag aktualisieren."""
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

            self.bearbeite_eintrag['medikament'] = med
            self.bearbeite_eintrag['fach'] = fach
            self.bearbeite_eintrag['tag'] = tag
            self.bearbeite_eintrag['zeit'] = zeit
            self.bearbeite_eintrag['anzahl'] = int(anzahl)

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

        eintrag = {
            'medikament': med,
            'fach': fach,
            'tag': tag,
            'zeit': zeit,
            'anzahl': anzahl_int
        }

        app.plan_eintraege.append(eintrag)

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
        self.fach_info_label.text = 'Fach: (noch nichts gewählt)'
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
