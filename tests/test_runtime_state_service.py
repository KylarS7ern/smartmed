import unittest

from smartmed.services.runtime_state_service import reset_runtime_state


class DummyApp:
    def __init__(self):
        self.offene_einnahmen = [{"irgendwas": 1}]
        self._last_popup_minute = "2026-04-19 10:30"


class RuntimeStateServiceTests(unittest.TestCase):
    def test_reset_runtime_state_resets_last_popup_minute(self):
        app = DummyApp()

        reset_runtime_state(app)

        self.assertIsNone(app._last_popup_minute)

    def test_reset_runtime_state_does_not_touch_offene_einnahmen(self):
        """offene_einnahmen wird pro Benutzer persistiert und darf beim
        Reset des Laufzeitzustands nicht mehr verworfen werden."""
        app = DummyApp()

        reset_runtime_state(app)

        self.assertEqual(app.offene_einnahmen, [{"irgendwas": 1}])


if __name__ == "__main__":
    unittest.main()