from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView


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
            zeit = e.get('zeit', '')
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