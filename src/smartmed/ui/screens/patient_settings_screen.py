from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from smartmed.ui import theme
from smartmed.ui.navigation import go_to_settings_menu
from smartmed.ui.widgets import (
    BodyLabel,
    SecondaryButton,
    StyledTextInput,
    SuccessButton,
    TitleLabel,
    field_row,
)
from smartmed.services.patient_profile_service import (
    apply_patient_profile_update,
    build_patient_form_data,
    build_patient_profile_update,
)


class PatientSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        outer = BoxLayout(orientation='vertical', padding=theme.PADDING, spacing=theme.SPACING)

        titel = TitleLabel(
            text='Patienten-Einstellungen',
            font_size=theme.FONT_XLARGE,
            size_hint=(1, None),
            height=dp(48)
        )

        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation='vertical', spacing=theme.SPACING, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.name_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.geburt_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)

        lbl_address = BodyLabel(
            text='Adresse:',
            font_size=theme.FONT_SMALL,
            size_hint=(1, None),
            height=dp(28)
        )
        self.address_input = StyledTextInput(multiline=True, font_size=theme.FONT_BODY, size_hint=(1, None), height=dp(90))

        self.doc_name_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.doc_email_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.doc_phone_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)

        self.c1_name_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.c1_email_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.c1_phone_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)

        self.c2_name_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.c2_email_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)
        self.c2_phone_input = StyledTextInput(multiline=False, font_size=theme.FONT_BODY)

        form.add_widget(field_row('Name:', self.name_input))
        form.add_widget(field_row('Geburtsdatum:', self.geburt_input))
        form.add_widget(lbl_address)
        form.add_widget(self.address_input)
        form.add_widget(field_row('Arzt (Name):', self.doc_name_input))
        form.add_widget(field_row('Arzt E-Mail:', self.doc_email_input))
        form.add_widget(field_row('Arzt Telefon:', self.doc_phone_input))
        form.add_widget(field_row('Kontakt 1 Name:', self.c1_name_input))
        form.add_widget(field_row('Kontakt 1 E-Mail:', self.c1_email_input))
        form.add_widget(field_row('Kontakt 1 Telefon:', self.c1_phone_input))
        form.add_widget(field_row('Kontakt 2 Name:', self.c2_name_input))
        form.add_widget(field_row('Kontakt 2 E-Mail:', self.c2_email_input))
        form.add_widget(field_row('Kontakt 2 Telefon:', self.c2_phone_input))

        scroll.add_widget(form)

        btn_speichern = SuccessButton(
            text='Patientendaten speichern',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_speichern.bind(on_press=self.speichern_patient)

        btn_back = SecondaryButton(
            text='Zurück',
            font_size=theme.FONT_LARGE,
            size_hint=(1, None),
            height=theme.BUTTON_HEIGHT
        )
        btn_back.bind(on_press=self.zurueck)

        outer.add_widget(titel)
        outer.add_widget(scroll)
        outer.add_widget(btn_speichern)
        outer.add_widget(btn_back)

        self.add_widget(outer)

    def on_pre_enter(self, *args):
        """Beim Öffnen aktuelle Daten laden."""
        app = App.get_running_app()
        form_data = build_patient_form_data(app)

        self.name_input.text = form_data['patient_name']
        self.geburt_input.text = form_data['patient_geburt']
        self.address_input.text = form_data['patient_address']
        self.doc_name_input.text = form_data['doctor_name']
        self.doc_email_input.text = form_data['doctor_email']
        self.doc_phone_input.text = form_data['doctor_phone']
        self.c1_name_input.text = form_data['contact1_name']
        self.c1_email_input.text = form_data['contact1_email']
        self.c1_phone_input.text = form_data['contact1_phone']
        self.c2_name_input.text = form_data['contact2_name']
        self.c2_email_input.text = form_data['contact2_email']
        self.c2_phone_input.text = form_data['contact2_phone']

    def speichern_patient(self, instance):
        app = App.get_running_app()

        profile_update = build_patient_profile_update(
            patient_name=self.name_input.text,
            patient_geburt=self.geburt_input.text,
            patient_address=self.address_input.text,
            doctor_name=self.doc_name_input.text,
            doctor_email=self.doc_email_input.text,
            doctor_phone=self.doc_phone_input.text,
            contact1_name=self.c1_name_input.text,
            contact1_email=self.c1_email_input.text,
            contact1_phone=self.c1_phone_input.text,
            contact2_name=self.c2_name_input.text,
            contact2_email=self.c2_email_input.text,
            contact2_phone=self.c2_phone_input.text,
        )

        apply_patient_profile_update(app, profile_update)
        app.save_data()

        print(
            'Patientendaten gespeichert:',
            app.patient_name,
            app.patient_geburt,
        )

    def zurueck(self, instance):
        app = App.get_running_app()
        go_to_settings_menu(app)
