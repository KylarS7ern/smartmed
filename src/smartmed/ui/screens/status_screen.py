from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from smartmed.ui import theme
from smartmed.ui.navigation import go_to_menu
from smartmed.ui.widgets import BodyLabel, MutedLabel, PrimaryButton, SecondaryButton, TitleLabel
from smartmed.services.schedule_service import WOCHENTAGE, ist_eintrag_faellig_am


class StatusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tages_offset = 0

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Status',
            font_size=theme.FONT_TITLE,
            size_hint=(1, 0.1)
        )

        self.datetime_label = MutedLabel(
            text='',
            font_size=theme.FONT_BODY,
            size_hint=(1, 0.08)
        )

        nav_layout = BoxLayout(
            orientation='horizontal',
            spacing=theme.SPACING,
            size_hint=(1, 0.1)
        )

        btn_prev = PrimaryButton(
            text='< Tag zurück',
            size_hint=(0.4, 1)
        )
        btn_prev.bind(on_press=self.tag_zurueck)

        btn_heute = SecondaryButton(
            text='Heute',
            size_hint=(0.2, 1)
        )
        btn_heute.bind(on_press=self.springe_zu_heute)

        btn_next = PrimaryButton(
            text='Tag vor >',
            size_hint=(0.4, 1)
        )
        btn_next.bind(on_press=self.tag_vor)

        nav_layout.add_widget(btn_prev)
        nav_layout.add_widget(btn_heute)
        nav_layout.add_widget(btn_next)

        self.status_label = BodyLabel(
            text='Lade Status...',
            font_size=theme.FONT_LARGE,
            halign='center',
            valign='middle',
            size_hint=(1, 0.57),
            markup=True,
        )

        btn_back = SecondaryButton(
            text='Zurück zum Hauptmenü',
            font_size=theme.FONT_LARGE,
            size_hint=(1, 0.13)
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

    def _primary_hex(self):
        r, g, b, _a = theme.PRIMARY
        return f"{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def update_status(self):
        """Status-text aus dem App-Zustand aktualisieren."""
        app = App.get_running_app()
        name = getattr(app, 'patient_name', 'Unbekannt')
        geburt = getattr(app, 'patient_geburt', '-')

        heute = datetime.now().date()
        zieldatum = heute + timedelta(days=self.tages_offset)

        tag_kurz = WOCHENTAGE[zieldatum.weekday()]
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
        eintraege_heute = [e for e in plan if ist_eintrag_faellig_am(e, zieldatum)]

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
            plan_text = 'Keine Einnahmen geplant.'

        primary_hex = self._primary_hex()
        eintrag_next, dt_next = app.naechste_einnahme()
        if eintrag_next and dt_next:
            med_next = eintrag_next.get('medikament', '')
            fach_next = eintrag_next.get('fach', '')
            anzahl_next = eintrag_next.get('anzahl', 1)

            next_tag_kurz = WOCHENTAGE[dt_next.weekday()]
            next_time_str = f"{next_tag_kurz} {dt_next.strftime('%d.%m.%Y %H:%M')}"
            next_line = (
                f'\n[b][color={primary_hex}]Nächste Einnahme: {next_time_str} | '
                f'Fach {fach_next} | {med_next} (x{anzahl_next})[/color][/b]'
            )
        else:
            next_line = '\nNächste Einnahme: keine geplant.'

        self.status_label.text = (
            f"Patient: {name}\n"
            f"Geburt: {geburt}\n\n"
            f"[b]Tag: {tag_kurz} {datum_str} {zusatz}[/b]\n\n"
            f"{plan_text}"
            f"{next_line}"
        )

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)

    def tag_zurueck(self, instance):
        """Einen Tag zurück blättern."""
        self.tages_offset -= 1
        self.update_status()

    def tag_vor(self, instance):
        """Einen Tag vor blättern."""
        self.tages_offset += 1
        self.update_status()

    def springe_zu_heute(self, instance):
        """Direkt zum heutigen Tag zurückspringen."""
        self.tages_offset = 0
        self.update_status()
