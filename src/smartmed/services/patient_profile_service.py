PROFILE_FIELDS = (
    'patient_name',
    'patient_geburt',
    'patient_address',
    'doctor_name',
    'doctor_email',
    'doctor_phone',
    'contact1_name',
    'contact1_email',
    'contact1_phone',
    'contact2_name',
    'contact2_email',
    'contact2_phone',
)


def build_patient_form_data(app):
    """Lädt die aktuellen Patientendaten aus der App für das UI."""
    data = {}

    for field_name in PROFILE_FIELDS:
        data[field_name] = str(getattr(app, field_name, '') or '')

    return data


def build_patient_profile_update(
    *,
    patient_name,
    patient_geburt,
    patient_address,
    doctor_name,
    doctor_email,
    doctor_phone,
    contact1_name,
    contact1_email,
    contact1_phone,
    contact2_name,
    contact2_email,
    contact2_phone,
):
    """Normalisiert die Eingaben aus dem Formular."""
    return {
        'patient_name': (patient_name or '').strip() or 'Demo-Patient',
        'patient_geburt': (patient_geburt or '').strip() or '-',
        'patient_address': (patient_address or '').strip(),
        'doctor_name': (doctor_name or '').strip(),
        'doctor_email': (doctor_email or '').strip(),
        'doctor_phone': (doctor_phone or '').strip(),
        'contact1_name': (contact1_name or '').strip(),
        'contact1_email': (contact1_email or '').strip(),
        'contact1_phone': (contact1_phone or '').strip(),
        'contact2_name': (contact2_name or '').strip(),
        'contact2_email': (contact2_email or '').strip(),
        'contact2_phone': (contact2_phone or '').strip(),
    }


def apply_patient_profile_update(app, profile_update):
    """Schreibt normalisierte Patientendaten zurück in die App."""
    for field_name, value in profile_update.items():
        setattr(app, field_name, value)