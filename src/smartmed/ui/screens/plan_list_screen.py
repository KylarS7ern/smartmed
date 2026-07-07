from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.ui import theme
from smartmed.ui.navigation import go_to_menu, go_to_plan_edit
from smartmed.ui.widgets import (
    BodyLabel,
    DangerButton,
    MutedLabel,
    PrimaryButton,
    SecondaryButton,
    SuccessButton,
    TitleLabel,
    make_popup,
)
from smartmed.services.plan_service import (
    delete_plan_entry,
    format_plan_entry_summary,
    plan_entry_sort_key,
)


class PlanListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.anzeige_eintraege = []

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Einnahmeplan',
            size_hint=(1, 0.13)
        )

        scroll = ScrollView(
            size_hint=(1, 0.65)
        )

        self.list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=theme.SPACING
        )

        self.list_layout.bind(
            minimum_height=self.list_layout.setter('height')
        )

        scroll.add_widget(self.list_layout)

        btn_neu = PrimaryButton(
            text='Neuen Eintrag anlegen',
            font_size=theme.FONT_LARGE,
            size_hint=(1, 0.11)
        )
        btn_neu.bind(on_press=self.neuer_eintrag)

        btn_back = SecondaryButton(
            text='Zurück zum Hauptmenü',
            font_size=theme.FONT_LARGE,
            size_hint=(1, 0.11)
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
            hinweis = MutedLabel(
                text='Keine Einträge vorhanden.',
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(40)
            )
            self.list_layout.add_widget(hinweis)
            return

        plan_sortiert = sorted(plan, key=plan_entry_sort_key)
        self.anzeige_eintraege = plan_sortiert

        for index, e in enumerate(plan_sortiert):
            text = format_plan_entry_summary(e)

            btn = PrimaryButton(
                text=text,
                font_size=theme.FONT_BODY,
                size_hint_y=None,
                height=dp(68),
                halign='center'
            )

            btn.bind(
                size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(40), None))
            )

            btn.bind(on_press=lambda inst, idx=index: self.eintrag_geklickt(idx))

            self.list_layout.add_widget(btn)

    def eintrag_geklickt(self, index):
        """Wird aufgerufen, wenn ein Eintrag-Button angetippt wird."""
        app = App.get_running_app()

        if index < 0 or index >= len(self.anzeige_eintraege):
            return

        eintrag = self.anzeige_eintraege[index]
        text = format_plan_entry_summary(eintrag).replace(' | ', '\n')

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=text,
            halign='center',
            valign='middle'
        )

        btn_layout = BoxLayout(orientation='horizontal', spacing=theme.SPACING, size_hint=(1, 0.3))

        btn_bearbeiten = PrimaryButton(text='Bearbeiten')
        btn_loeschen = DangerButton(text='Löschen')
        btn_abbrechen = SecondaryButton(text='Abbrechen')

        btn_layout.add_widget(btn_bearbeiten)
        btn_layout.add_widget(btn_loeschen)
        btn_layout.add_widget(btn_abbrechen)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Eintrag', content=layout, size_hint=(0.85, 0.5))

        def loeschen_bestaetigt(_instance):
            result = delete_plan_entry(
                plan_eintraege=app.plan_eintraege,
                eintrag=eintrag,
            )

            app.fach_medikamente = result['fach_medikamente']

            if result['ok']:
                app.log_event(result['log_text'])
            else:
                print(result['message'])

            self.update_liste()
            popup.dismiss()

        def loeschen_nachfragen(_instance):
            popup.dismiss()
            self._zeige_loesch_bestaetigung(eintrag, loeschen_bestaetigt)

        def bearbeiten(_instance):
            app = App.get_running_app()
            popup.dismiss()
            go_to_plan_edit(app, eintrag)

        btn_loeschen.bind(on_press=loeschen_nachfragen)
        btn_bearbeiten.bind(on_press=bearbeiten)
        btn_abbrechen.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def _zeige_loesch_bestaetigung(self, eintrag, on_bestaetigt):
        """Zweite, ausdrückliche Sicherheitsabfrage vor dem endgültigen Löschen."""
        text = format_plan_entry_summary(eintrag)

        layout = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        label = BodyLabel(
            text=f"Eintrag wirklich endgültig löschen?\n\n{text}",
            halign='center',
            valign='middle'
        )

        btn_layout = BoxLayout(orientation='horizontal', spacing=theme.SPACING, size_hint=(1, 0.3))

        btn_ja = DangerButton(text='Ja, löschen')
        btn_nein = SecondaryButton(text='Nein')

        btn_layout.add_widget(btn_ja)
        btn_layout.add_widget(btn_nein)

        layout.add_widget(label)
        layout.add_widget(btn_layout)

        popup = make_popup(title='Löschen bestätigen', content=layout, size_hint=(0.85, 0.5))

        def ja(_instance):
            popup.dismiss()
            on_bestaetigt(None)

        btn_ja.bind(on_press=ja)
        btn_nein.bind(on_press=lambda *_: popup.dismiss())

        popup.open()

    def neuer_eintrag(self, instance):
        app = App.get_running_app()
        go_to_plan_edit(app)

    def zurueck_zum_menue(self, instance):
        app = App.get_running_app()
        go_to_menu(app)
