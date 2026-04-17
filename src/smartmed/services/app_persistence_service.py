from smartmed.models.defaults import build_default_user


def apply_loaded_data(app, data: dict) -> None:
    """Überträgt geladene JSON-Daten in den App-Zustand."""
    app.fach_medikamente = data.get("fach_medikamente", {})
    app.admin_pin = data.get("admin_pin", "")

    if "users" in data:
        app.users = data.get("users", {})
        app.current_user = data.get("current_user")
    else:
        default_user = build_default_user(
            username="Standard",
            password="",
            patient_name=data.get("patient_name", app.patient_name),
            patient_geburt=data.get("patient_geburt", app.patient_geburt),
            settings=data.get("settings", app.settings),
        )
        default_user["plan_eintraege"] = data.get("plan_eintraege", [])
        default_user["log_eintraege"] = data.get("log_eintraege", [])

        app.users = {"Standard": default_user}
        app.current_user = "Standard"

    if not app.users:
        app.users = {
            "Standard": build_default_user(
                username="Standard",
                password="",
                patient_name=app.patient_name,
                patient_geburt=app.patient_geburt,
                settings=app.settings,
            )
        }
        app.current_user = "Standard"

    if not app.current_user or app.current_user not in app.users:
        app.current_user = sorted(app.users.keys())[0]


def build_data_to_save(app) -> dict:
    """Erzeugt die persistierbare Datenstruktur aus dem aktuellen App-Zustand."""
    return {
        "fach_medikamente": app.fach_medikamente,
        "users": app.users,
        "current_user": app.current_user,
        "admin_pin": app.admin_pin,
    }
