def build_default_settings() -> dict:
    return {
        "alarm_delay_min": 30,
        "alarm_mode": "popup",
        "notify_mode": "none",
        "email_to": "",
        "telegram_chat_id": "",
        "email_recipient": "manual",
    }


def build_default_user(
    username: str = "Standard",
    password: str = "",
    patient_name: str | None = None,
    patient_geburt: str = "-",
    settings: dict | None = None,
) -> dict:
    return {
        "password": password,
        "patient_name": patient_name or username,
        "patient_geburt": patient_geburt,
        "patient_address": "",
        "doctor_name": "",
        "doctor_email": "",
        "doctor_phone": "",
        "contact1_name": "",
        "contact1_email": "",
        "contact1_phone": "",
        "contact2_name": "",
        "contact2_email": "",
        "contact2_phone": "",
        "settings": dict(settings) if settings is not None else build_default_settings(),
        "plan_eintraege": [],
        "log_eintraege": [],
        "offene_einnahmen": [],
    }

def build_default_app_state() -> dict:
    return {
        "patient_name": "Demo-Patient",
        "patient_geburt": "01.01.2000",
        "plan_eintraege": [],
        "fach_medikamente": {},
        "log_eintraege": [],
        "offene_einnahmen": [],
        "patient_address": "",
        "doctor_name": "",
        "doctor_email": "",
        "doctor_phone": "",
        "contact1_name": "",
        "contact1_email": "",
        "contact1_phone": "",
        "contact2_name": "",
        "contact2_email": "",
        "contact2_phone": "",
        "admin_pin": "",
        "settings": build_default_settings(),
        "users": {},
        "current_user": None,
    }