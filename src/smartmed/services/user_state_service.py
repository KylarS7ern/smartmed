from smartmed.services.schedule_service import (
    deserialize_offene_einnahmen,
    serialize_offene_einnahmen,
)


def load_user_into_app(app, username):
    """Lädt die Daten eines Benutzers in die App-Attribute."""
    user = app.users.get(username, {})

    app.patient_name = user.get('patient_name', 'Demo-Patient')
    app.patient_geburt = user.get('patient_geburt', '01.01.2000')

    app.patient_address = user.get('patient_address', user.get('patient_adress', ''))
    app.doctor_name = user.get('doctor_name', '')
    app.doctor_email = user.get('doctor_email', '')
    app.doctor_phone = user.get('doctor_phone', '')
    app.contact1_name = user.get('contact1_name', '')
    app.contact1_email = user.get('contact1_email', '')
    app.contact1_phone = user.get('contact1_phone', '')
    app.contact2_name = user.get('contact2_name', '')
    app.contact2_email = user.get('contact2_email', '')
    app.contact2_phone = user.get('contact2_phone', '')

    app.settings.update(user.get('settings', {}))

    app.plan_eintraege = user.get('plan_eintraege', [])
    app.log_eintraege = user.get('log_eintraege', [])
    app.offene_einnahmen = deserialize_offene_einnahmen(user.get('offene_einnahmen', []))


def store_current_user_state(app):
    """Schreibt die aktuellen App-Attribute zurück in den aktiven Benutzer."""
    if app.current_user is None:
        return

    user = app.users.setdefault(app.current_user, {})

    user.setdefault('password', '')

    user['patient_name'] = app.patient_name
    user['patient_geburt'] = app.patient_geburt

    user['patient_address'] = app.patient_address
    user['doctor_name'] = app.doctor_name
    user['doctor_email'] = app.doctor_email
    user['doctor_phone'] = app.doctor_phone
    user['contact1_name'] = app.contact1_name
    user['contact1_email'] = app.contact1_email
    user['contact1_phone'] = app.contact1_phone
    user['contact2_name'] = app.contact2_name
    user['contact2_email'] = app.contact2_email
    user['contact2_phone'] = app.contact2_phone

    user['settings'] = app.settings.copy()
    user['plan_eintraege'] = app.plan_eintraege
    user['log_eintraege'] = app.log_eintraege
    user['offene_einnahmen'] = serialize_offene_einnahmen(app.offene_einnahmen)
