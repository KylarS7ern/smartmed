from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class StatusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tages_offset = 0

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
            zusatz = 'gestern'
        else:
            zusatz = f"({self.tages_offset:+d} Tage)"

        plan = getattr(app, 'plan_eintraege', [])
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
            next_line = (
                f'\nNächste Einnahme: {next_time_str} | '
                f'Fach {fach_next} | {med_next} (x{anzahl_next})'
            )
        else:
            next_line = '\nNächste Einnahme: keine geplant.'

        self.status_label.text = (
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
