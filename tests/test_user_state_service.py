import unittest
from datetime import datetime

from smartmed.services.user_state_service import load_user_into_app, store_current_user_state


class DummyApp:
    def __init__(self, users=None, current_user=None):
        self.users = users or {}
        self.current_user = current_user
        self.settings = {}
        self.offene_einnahmen = []
        for feld in (
            "patient_name", "patient_geburt", "patient_address",
            "doctor_name", "doctor_email", "doctor_phone",
            "contact1_name", "contact1_email", "contact1_phone",
            "contact2_name", "contact2_email", "contact2_phone",
        ):
            setattr(self, feld, "")
        self.plan_eintraege = []
        self.log_eintraege = []


class UserStateServiceOffeneEinnahmenTests(unittest.TestCase):
    def test_load_user_into_app_restores_offene_einnahmen(self):
        users = {
            "Anna": {
                "offene_einnahmen": [{
                    "key": ["Mo", "08:00", "1", "A", "2026-04-20"],
                    "eintrag": {"medikament": "A"},
                    "faellige_zeit": "2026-04-20T08:00:00",
                    "deadline": "2026-04-20T08:30:00",
                    "bestaetigt": False,
                    "alarm_verschickt": False,
                }]
            }
        }
        app = DummyApp(users=users)

        load_user_into_app(app, "Anna")

        self.assertEqual(len(app.offene_einnahmen), 1)
        self.assertEqual(
            app.offene_einnahmen[0]["key"], ("Mo", "08:00", "1", "A", "2026-04-20")
        )
        self.assertEqual(
            app.offene_einnahmen[0]["faellige_zeit"], datetime(2026, 4, 20, 8, 0, 0)
        )

    def test_load_user_into_app_defaults_to_empty_list_for_old_data(self):
        users = {"Anna": {}}
        app = DummyApp(users=users)

        load_user_into_app(app, "Anna")

        self.assertEqual(app.offene_einnahmen, [])

    def test_store_current_user_state_serializes_offene_einnahmen(self):
        app = DummyApp(users={"Anna": {}}, current_user="Anna")
        app.offene_einnahmen = [{
            "key": ("Mo", "08:00", "1", "A", "2026-04-20"),
            "eintrag": {},
            "faellige_zeit": datetime(2026, 4, 20, 8, 0, 0),
            "deadline": datetime(2026, 4, 20, 8, 30, 0),
            "bestaetigt": False,
            "alarm_verschickt": False,
        }]

        store_current_user_state(app)

        gespeichert = app.users["Anna"]["offene_einnahmen"]
        self.assertEqual(gespeichert[0]["key"], ["Mo", "08:00", "1", "A", "2026-04-20"])
        self.assertEqual(gespeichert[0]["faellige_zeit"], "2026-04-20T08:00:00")

    def test_store_current_user_state_does_nothing_without_current_user(self):
        app = DummyApp(users={}, current_user=None)

        store_current_user_state(app)

        self.assertEqual(app.users, {})

    def test_round_trip_survives_switch_user_style_save_and_load(self):
        """Simuliert store -> load (wie bei switch_user/Neustart) und
        stellt sicher, dass eine offene Einnahme dabei nicht verschwindet."""
        app = DummyApp(users={"Anna": {}}, current_user="Anna")
        app.offene_einnahmen = [{
            "key": ("Mo", "08:00", "1", "A", "2026-04-20"),
            "eintrag": {"medikament": "A"},
            "faellige_zeit": datetime(2026, 4, 20, 8, 0, 0),
            "deadline": datetime(2026, 4, 20, 8, 30, 0),
            "bestaetigt": False,
            "alarm_verschickt": False,
        }]

        store_current_user_state(app)
        app.offene_einnahmen = []
        load_user_into_app(app, "Anna")

        self.assertEqual(len(app.offene_einnahmen), 1)
        self.assertFalse(app.offene_einnahmen[0]["bestaetigt"])


if __name__ == "__main__":
    unittest.main()
