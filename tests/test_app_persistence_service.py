import unittest
from types import SimpleNamespace

from smartmed.services.app_persistence_service import build_data_to_save


class AppPersistenceServiceTests(unittest.TestCase):
    def test_build_data_to_save_excludes_runtime_state(self):
        app = SimpleNamespace(
            fach_medikamente={"1": "Aspirin"},
            users={"Standard": {"patient_name": "Max"}},
            current_user="Standard",
            admin_pin="1234",
            offene_einnahmen=[{"test": 1}],
            _last_popup_minute="2026-04-19 10:30",
        )

        data = build_data_to_save(app)

        self.assertIn("fach_medikamente", data)
        self.assertIn("users", data)
        self.assertIn("current_user", data)
        self.assertIn("admin_pin", data)

        self.assertNotIn("offene_einnahmen", data)
        self.assertNotIn("_last_popup_minute", data)


if __name__ == "__main__":
    unittest.main()