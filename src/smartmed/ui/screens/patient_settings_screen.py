from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from smartmed.ui.navigation import go_to_settings_menu
from smartmed.services.patient_profile_service import (
    apply_patient_profile_update,
    build_patient_form_data,
    build_patient_profile_update,
)

class PatientSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        titel = Label(
            text='Patienten-Einstellungen',
            font_size='24sp',
            size_hint=(1, 0.15)
        )

        name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_name = Label(
            text='Name:',
            size_hint=(0.4, 1)
        )
        self.name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        name_layout.add_widget(lbl_name)
        name_layout.add_widget(self.name_input)

        geburt_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_geburt = Label(
            text='Geburtsdatum:',
            size_hint=(0.4, 1)
        )
        self.geburt_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        geburt_layout.add_widget(lbl_geburt)
        geburt_layout.add_widget(self.geburt_input)

        lbl_address = Label(
            text='Adresse:',
            size_hint=(1, 0.1)
        )
        self.address_input = TextInput(
            multiline=True,
            size_hint=(1, 0.25)
        )

        doc_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_name = Label(
            text='Arzt (Name):',
            size_hint=(0.4, 1)
        )
        self.doc_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_name_layout.add_widget(lbl_doc_name)
        doc_name_layout.add_widget(self.doc_name_input)

        doc_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_email = Label(
            text='Arzt E-Mail:',
            size_hint=(0.4, 1)
        )
        self.doc_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_email_layout.add_widget(lbl_doc_email)
        doc_email_layout.add_widget(self.doc_email_input)

        doc_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_doc_phone = Label(
            text='Arzt Telefon:',
            size_hint=(0.4, 1)
        )
        self.doc_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        doc_phone_layout.add_widget(lbl_doc_phone)
        doc_phone_layout.add_widget(self.doc_phone_input)

        c1_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_name = Label(
            text='Kontakt 1 Name:',
            size_hint=(0.4, 1)
        )
        self.c1_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_name_layout.add_widget(lbl_c1_name)
        c1_name_layout.add_widget(self.c1_name_input)

        c1_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_email = Label(
            text='Kontakt 1 E-Mail:',
            size_hint=(0.4, 1)
        )
        self.c1_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_email_layout.add_widget(lbl_c1_email)
        c1_email_layout.add_widget(self.c1_email_input)

        c1_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c1_phone = Label(
            text='Kontakt 1 Telefon:',
            size_hint=(0.4, 1)
        )
        self.c1_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c1_phone_layout.add_widget(lbl_c1_phone)
        c1_phone_layout.add_widget(self.c1_phone_input)

        c2_name_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_name = Label(
            text='Kontakt 2 Name:',
            size_hint=(0.4, 1)
        )
        self.c2_name_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_name_layout.add_widget(lbl_c2_name)
        c2_name_layout.add_widget(self.c2_name_input)

        c2_email_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_email = Label(
            text='Kontakt 2 E-Mail:',
            size_hint=(0.4, 1)
        )
        self.c2_email_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_email_layout.add_widget(lbl_c2_email)
        c2_email_layout.add_widget(self.c2_email_input)

        c2_phone_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, 0.1)
        )
        lbl_c2_phone = Label(
            text='Kontakt 2 Telefon:',
            size_hint=(0.4, 1)
        )
        self.c2_phone_input = TextInput(
            multiline=False,
            size_hint=(0.6, 1)
        )
        c2_phone_layout.add_widget(lbl_c2_phone)
        c2_phone_layout.add_widget(self.c2_phone_input)

        btn_speichern = Button(
            text='Patientendaten speichern',
            size_hint=(1, 0.12)
        )
        btn_speichern.bind(on_press=self.speichern_patient)

        btn_back = Button(
            text='Zurück',
            size_hint=(1, 0.2)
        )
        btn_back.bind(on_press=self.zurueck)

        layout.add_widget(titel)
        layout.add_widget(name_layout)
        layout.add_widget(geburt_layout)
        layout.add_widget(lbl_address)
        layout.add_widget(self.address_input)
        layout.add_widget(doc_name_layout)
        layout.add_widget(doc_email_layout)
        layout.add_widget(doc_phone_layout)
        layout.add_widget(c1_name_layout)
        layout.add_widget(c1_email_layout)
        layout.add_widget(c1_phone_layout)
        layout.add_widget(c2_name_layout)
        layout.add_widget(c2_email_layout)
        layout.add_widget(c2_phone_layout)
        layout.add_widget(btn_speichern)
        layout.add_widget(btn_back)

        self.add_widget(layout)

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
