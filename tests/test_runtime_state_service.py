import unittest

from smartmed.services.runtime_state_service import reset_runtime_state


class DummyApp:
    def __init__(self):
        self.offene_einnahmen = [{"irgendwas": 1}]
        self._last_popup_minute = "2026-04-19 10:30"


class RuntimeStateServiceTests(unittest.TestCase):
    def test_reset_runtime_state_resets_transient_fields(self):
        app = DummyApp()

        reset_runtime_state(app)

        self.assertEqual(app.offene_einnahmen, [])
        self.assertIsNone(app._last_popup_minute)


if __name__ == "__main__":
    unittest.main()